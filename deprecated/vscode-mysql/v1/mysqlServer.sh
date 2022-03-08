#!/bin/bash
# This script depends on environment variables "WORKSPACE_MODE" and "WORKSPACE_TYPE" that comes from WorkspaceEnvironmentVariablesManager

# Initialize and start mysql server on container launch
##########  This seciton of mysql set up helpers are mostly copied from the official mysql docker image: https://github.com/docker-library/mysql/blob/master/8.0/docker-entrypoint.sh
set -eo pipefail
shopt -s nullglob

# logging functions
mysql_log() {
    local type="$1"; shift
    printf '%s [%s] [Entrypoint]: %s\n' "$(date --rfc-3339=seconds)" "$type" "$*"
}
mysql_note() {
    mysql_log Note "$@"
}
mysql_warn() {
    mysql_log Warn "$@" >&2
}
mysql_error() {
    mysql_log ERROR "$@" >&2
    exit 1
}

mysql_check_config() {
    local toRun=( "$@" --verbose --help ) errors
    if ! errors="$("${toRun[@]}" 2>&1 >/dev/null)"; then
        mysql_error $'mysqld failed while attempting to check config\n\tcommand was: '"${toRun[*]}"$'\n\t'"$errors"
    fi
}

# Fetch value from server config
# We use mysqld --verbose --help instead of my_print_defaults because the
# latter only show values present in config files, and not server defaults
mysql_get_config() {
    local conf="$1"; shift
    "$@" --verbose --help --log-bin-index="$(mktemp -u)" 2>/dev/null \
        | awk -v conf="$conf" '$1 == conf && /^[^ \t]/ { sub(/^[^ \t]+[ \t]+/, ""); print; exit }'
    # match "datadir      /some/path with/spaces in/it here" but not "--xyz=abc\n     datadir (xyz)"
}

# Do a temporary startup of the MySQL server, for init purposes
docker_temp_server_start() {
    # For 5.7+ the server is ready for use as soon as startup command unblocks
    if ! "$@" --daemonize --skip-networking --socket="${SOCKET}"; then
        mysql_error "Unable to start server."
    fi
}

# Stop the server. When using a local socket file mysqladmin will block until
# the shutdown is complete.
docker_temp_server_stop() {
    if ! mysqladmin shutdown -uroot --socket="${SOCKET}"; then
        mysql_error "Unable to shut down server."
    fi
}

# initializes the database directory
docker_init_database_dir() {
    if [ -z "$(ls -A "$DATADIR")" ]; then
        mysql_note "Initializing database files"
        "$@" --initialize-insecure
        mysql_note "Database files initialized"
    fi
}

# Loads various settings that are used elsewhere in the script
# This should be called after mysql_check_config, but before any other functions
docker_setup_env() {
    # Get config
    declare -g DATADIR SOCKET
    DATADIR="$(mysql_get_config 'datadir' "$@")"
    SOCKET="$(mysql_get_config 'socket' "$@")"
    
    # Allow sql connection from vscode-sql extension
    export MYSQL_ROOT_HOST=%
    
    declare -g DATABASE_ALREADY_EXISTS
    if [ -d "$DATADIR/mysql" ]; then
        DATABASE_ALREADY_EXISTS='true'
    fi
}

# Execute sql script, passed via stdin
# usage: docker_process_sql [mysql-cli-args]
#    ie: docker_process_sql --database=mydb <<<'INSERT ...'
#    ie: docker_process_sql --database=mydb <my-file.sql
docker_process_sql() {
    # args sent in can override this db, since they will be later in the command
    if [ -n "$MYSQL_DATABASE" ]; then
        set -- --database="$MYSQL_DATABASE" "$@"
    fi
    mysql --protocol=socket -uroot -hlocalhost --socket="${SOCKET}" "$@"
}

# Initializes database with timezone info and root password, plus optional extra db/user
docker_setup_db() {
    # Sets root password and creates root users for non-localhost hosts
    local rootCreate=
    # default root to listen for connections from anywhere
    if [ -n "$MYSQL_ROOT_HOST" ] && [ "$MYSQL_ROOT_HOST" != 'localhost' ]; then
        read -r -d '' rootCreate <<-EOSQL || true
            CREATE USER 'root'@'${MYSQL_ROOT_HOST}' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}' ;
            GRANT ALL ON *.* TO 'root'@'${MYSQL_ROOT_HOST}' WITH GRANT OPTION ;
            # Create a coder user with all permissions
            # using mysql_native_password for a simpler auth method that works with vscode-mysql extension
            CREATE USER 'coder'@'${MYSQL_ROOT_HOST}' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}' ;
            GRANT ALL ON *.* TO 'coder'@'${MYSQL_ROOT_HOST}' WITH GRANT OPTION ;

EOSQL
    fi
    
    docker_process_sql --database=mysql <<-EOSQL
        -- What's done in this file shouldn't be replicated
        --  or products like mysql-fabric won't work
        SET @@SESSION.SQL_LOG_BIN=0;
        GRANT ALL ON *.* TO 'root'@'localhost' WITH GRANT OPTION ;
        FLUSH PRIVILEGES ;
        ${rootCreate}
        DROP DATABASE IF EXISTS test ;
EOSQL
}

######### End of mysql set up helpers

# Set up datadir
# Instructor workspace: Use defaul /var/lib/mysql as the datadir for mysql, this directory is mounted and all instructor changes will be saved
# Learner workspace:
#   When first time launching learner workspace (which is a copy from the template)
#       - Some files in datadir are made read-only when published the template, we will make a RW copy of these files since mysql needs them at runtime
#       - Move all datadir content to /var/lib/mysql/learner_mysql, then point mysql to use the learner datadir /var/lib/mysql/learner_mysql
#   For subsequent launches of learner workspace:
#       - Point mysql to use the learner datadir /var/lib/mysql/learner_mysql
# We are using a different path for learner datadir because the ro directory for the original datadir /var/lib/mysql-ro already contains
#   some files, this would conflict with current datadir content when we archive current datadir into /var/lib/mysql-ro when creating shared workspaces
data_dir_setup() {
    local dataro="${DATADIR::-1}-ro"
    local newdir="${DATADIR}learner_mysql"
    local copied=false

    if [ "$WORKSPACE_TYPE" = "student" ] ; then
	# Clean up the mounted directory if data has already been copied to newdir
	# The old datadir will have some repeated files if this container is launched after syncing instructor workspace by clicking 'get latest version'
	if [ -d "$newdir" ] ; then
	    local dups=$(find $DATADIR -mindepth 1 -maxdepth 0 ! -name "learner_mysql")
	    rm -rf "$dups"
            DATABASE_ALREADY_EXISTS='true'
	fi

        # Copy over the read-only files when first start learner workspace
        if [ -d "$dataro" ] & [ ! -d "$newdir" ] ; then
	    while read f; do
                local rwfile="${DATADIR}${f}"
                # check if any files in datadir are symlink to RO directory
                if [ -L "$rwfile" ] ; then
                    echo "Replacing symlink with concrete file: $rwfile..."
                    rm -f "$rwfile"
                    cp -p "${dataro}/${f}" "$rwfile"
                    copied=true
                fi
            done <<< $(find "$dataro" -type f | cut -sd /  -f 5-)
            
            if $copied ; then
                # Remove some log files and tmp files
                rm -f "${DATADIR}/undo_"*  "${DATADIR}/ibtmp"* "${DATADIR}/'#"*
                
                # Mysql server will have error if its system files have different create times
                mkdir /tmp/copy_sql
                cp -r "$DATADIR"/* /tmp/copy_sql
                rm -rf "$DATADIR"/*
                
                # Move all datadir content to a new path
                mkdir "$DATADIR"/learner_mysql
                cp -r /tmp/copy_sql/* "$newdir"
            fi
        fi

	# point mysql to use new datadir
        # We can append to my.cnf since mysql takes the last one of duplicated configs
	cat <<-EOF >> /etc/mysql/my.cnf

	datadir=${newdir}
	EOF
    fi
}

_main() {

    mysql_note "Entrypoint script for MySQL Server ${MYSQL_VERSION} started."
    
 
    if [ "$WORKSPACE_MODE" = "readonly" ]; then
    
        # move sql datadir from readonly dir to a new unmounted dir so that
        #   sql runtime files are writable, and modifications to files won't be saved
        mkdir /mnt/mysql_mount/mysql
        cp -a /var/lib/mysql-ro/learner_mysql/* /mnt/mysql_mount/mysql/
        
        # Point mysql config to the new datadir; run mysql with the new config file
        cp /etc/mysql/my.cnf /mnt/mysql_mount

	cat <<-EOF >> /mnt/mysql_mount/my.cnf

	datadir=/mnt/mysql_mount/mysql
	EOF

        exec "$@" --defaults-file=/mnt/mysql_mount/my.cnf
        
    else
        mysql_check_config "$@"
        
        # Load various environment variables
        docker_setup_env "$@"
        
        mkdir -p "$DATADIR"
        data_dir_setup
        
        # there's no database, so it needs to be initialized
        if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
            docker_init_database_dir "$@"

            mysql_note "Starting temporary server"
            docker_temp_server_start "$@"
            mysql_note "Temporary server started."

            docker_setup_db
            
            mysql_note "Stopping temporary server"
            docker_temp_server_stop
            mysql_note "Temporary server stopped"

            echo
            mysql_note "MySQL init process done. Ready for start up."
            echo
        fi
        exec "$@"
    fi
}

_main "$@"
