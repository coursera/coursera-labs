#!/usr/bin/env bash
su -c "/usr/local/bin/mysqlServer.sh mysqld &" coder

su -c "cp -n /tmp/launchButtonSettings.json /home/coder/coursera/" - coder
python3 ${VSCODE_USER}/coursera/refreshButtonConfig.py

# prevent the script from re-copying these files over in student lab
if [ "${WORKSPACE_TYPE}" = "instructor" ]; then
    # git in lab persistence + default options
    mkdir -p -m777 /home/coder/project/.dotfiles-coursera
    su -c "ln -s /home/coder/project/.dotfiles-coursera/.gitconfig /home/coder/.gitconfig" - coder
    su -c "ln -s /home/coder/project/.dotfiles-coursera/.git-credentials /home/coder/.git-credentials" - coder
    su -c "git config --global core.fileMode false" - coder

    # Hide certain files in the /home/coder/project directory
    su -c "cp -n /tmp/.hidden /home/coder/project/.hidden" - coder
fi

# initialize npm inside home directory
cd /home/coder/
npm init -y

# copy reverse-proxy default template into /home/nginx/ only if it doesn't exist
if [ ! -f /home/nginx/reverse-proxy.conf ]; then
    cp /etc/nginx/sites-enabled/reverse-proxy.conf.template /home/nginx/reverse-proxy.conf
    chmod a+w /home/nginx/reverse-proxy.conf
fi

# copy nginx and proxy-related files to /home/nginx/
su -c "cp -rn /tmp/nginx-files/. /home/nginx" - coder

# install nginx-conf npm package for reverse proxy config script
cd /home/nginx
su -c "npm install --global" - coder

# link reverse-proxy from mount point to location where it actually takes effect
ln -s /home/nginx/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf
export PATH=/home/npm-global/bin:$PATH

# link refreshButton script so it's more easily accessible
ln -s $VSCODE_USER/coursera/refreshButtonConfig.py /home/coder/coursera/refreshButtonConfig.py

/usr/bin/supervisord
