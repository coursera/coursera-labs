#!/bin/bash -x
### every exit != 0 fails the script
#set -e

## print out help
help (){
    echo "
    USAGE:
    docker run -it -p 6901:6901 -p 5901:5901 consol/<image>:<tag> <option>

    IMAGES:
    consol/ubuntu-xfce-vnc
    consol/centos-xfce-vnc
    consol/ubuntu-icewm-vnc
    consol/centos-icewm-vnc

    TAGS:
    latest  stable version of branch 'master'
    dev     current development version of branch 'dev'

    OPTIONS:
    -w, --wait      (default) keeps the UI and the vncserver up until SIGINT or SIGTERM will received
    -s, --skip      skip the vnc startup and just execute the assigned command.
                    example: docker run consol/centos-xfce-vnc --skip bash
    -d, --debug     enables more detailed startup output
                    e.g. 'docker run consol/centos-xfce-vnc --debug bash'
    -h, --help      print out this help

    Fore more information see: https://github.com/ConSol/docker-headless-vnc-container
    "
}

## correct forwarding of shutdown signal
cleanup () {
    kill -s SIGTERM $!
    exit 0
}

vnc_setup() {
    ## resolve_vnc_connection
    VNC_IP=$(hostname -i)

    ## change vnc password
    echo -e "\n------------------ change VNC password  ------------------"
    # first entry is control, second is view (if only one is valid for both)
    mkdir -p "$HOME/.vnc"
    PASSWD_PATH="$HOME/.vnc/passwd"

    if [[ -f $PASSWD_PATH ]]; then
        echo -e "\n---------  purging existing VNC password settings  ---------"
        rm -f $PASSWD_PATH
    fi

    if [[ $VNC_VIEW_ONLY == "true" ]]; then
        echo "start VNC server in VIEW ONLY mode!"
        #create random pw to prevent access
        echo $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 20) | vncpasswd -f > $PASSWD_PATH
    fi
    echo "$VNC_PW" | vncpasswd -f >> $PASSWD_PATH
    chmod 600 $PASSWD_PATH

    ## start vncserver and noVNC webclient
    echo -e "\n------------------ start noVNC  ----------------------------"
    if [[ $DEBUG == true ]]; then echo "$NO_VNC_HOME/utils/launch.sh --vnc localhost:$VNC_PORT --listen $NO_VNC_PORT"; fi
    $NO_VNC_HOME/utils/launch.sh --vnc localhost:$VNC_PORT --listen $NO_VNC_PORT &> $STARTUPDIR/no_vnc_startup.log & 
    PID_SUB=$!

    echo -e "\n------------------ start VNC server ------------------------"
    echo "remove old vnc locks to be a reattachable container"
    vncserver -kill $DISPLAY &> $STARTUPDIR/vnc_startup.log \
        || rm -rfv /tmp/.X*-lock /tmp/.X11-unix &> $STARTUPDIR/vnc_startup.log \
        || echo "no locks present"
}

browser_start(){
    ## write correct window size to chrome properties
    $STARTUPDIR/chrome-init.sh
    # Use default content path if not set
    IN_LAB_BROWSER_START_URL=${AWS_CLOUD_LAB_START_URL:-"https://www.coursera.org"}

    cat << EOF > ${HOME}/.config/openbox/autostart
    /usr/bin/chromium-browser --start-maximized --disable-signin-promo ${IN_LAB_BROWSER_START_URL} &
    sleep 2
    wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz &
EOF
}

vnc_startup(){
    echo -e "start vncserver with param: VNC_COL_DEPTH=$VNC_COL_DEPTH, VNC_RESOLUTION=$VNC_RESOLUTION\n..."
    if [[ $DEBUG == true ]]; then echo "vncserver $DISPLAY -depth $VNC_COL_DEPTH -geometry $VNC_RESOLUTION"; fi
    vncserver $DISPLAY -depth $VNC_COL_DEPTH -geometry $VNC_RESOLUTION -xstartup /usr/bin/openbox-session  &> $STARTUPDIR/no_vnc_startup.log
    echo -e "start window manager\n..."
}

# Function to check and maximize the most recently active chromium browser window 
window_maximize_check() {
  
  # Get the list of window IDs for Chromium instances 
  raw_window_list=$(wmctrl -l -p | grep $(pgrep -o chromium))

# For each window, retrieve the time of last user activity on the window
  while read -r id; do 
    user_time=$(xprop -id $id _NET_WM_USER_TIME | awk '{print $3}')
  done <<< "$(echo "$raw_window_list" | awk '{print $1}')"

  # Identify the window ID of the most recently accessed window by sorting them based on _NET_WM_USER_TIME
  window_id=$(echo "$raw_window_list" | awk '{print $1}' | while read id; do 
    echo "$id $(xprop -id $id _NET_WM_USER_TIME | awk '{print $3}')"; 
  done | sort -nk 2 | tail -n 1 | awk '{print $1}')

  # Checks if the window_id variable exists
  if [ -n "$window_id" ]; then
    # Fetches the title of the window using the window id
    window_title=$(wmctrl -l -p | grep -w $window_id | awk '{$1=$2=$3=""; print $0}')  

    # Retrieves window properties "_NET_WM_STATE" and "window state" for the identified window
    resize_state=$(xprop -id $window_id | grep "_NET_WM_STATE(ATOM)")
    minimize_state=$(xprop -id $window_id | grep "window state")

    # Checks if the window doesn't have "Task Manager- Chromium" in its title (don't want this window maximized) and is not maximized (either vertically, horizontally or in iconic state)
    if [[ ! $window_title =~ "Task Manager - Chromium" ]] && [[ $resize_state != *"_NET_WM_STATE_MAXIMIZED_VERT"* || $resize_state != *"_NET_WM_STATE_MAXIMIZED_HORZ"* || $minimize_state == *"Iconic"* ]]; then
        echo "Chromium window $window_id is not maximized"
        wmctrl -i -r $window_id -b remove,hidden,shaded && wmctrl -i -r $window_id -b add,maximized_vert,maximized_horz
        echo " Chromium window $window_id is now maximized"
    fi
  else
    echo "No window ID obtained. Check previous steps."
  fi
}

start_chromium(){
    echo "Starting browser"
    /usr/bin/chromium-browser --start-maximized --disable-signin-promo --guest ${IN_LAB_BROWSER_START_URL} &
    wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz 
    wmctrl -a Chromium # activate (focus) the Chromium window
}

#!/bin/bash
function check_time_difference() {
  curr_timestamp=$(date +%s) # get current time in seconds
  last_timestamp=$(cat last_timestamp.txt) # read the last timestamp from a file

  # check if file is not empty and time difference is greater than 55 seconds
  if [[ -n "$last_timestamp" ]] && (( curr_timestamp - last_timestamp > 55 )); then
    xdotool mousemove_relative 1 1
    xdotool mousemove_relative -- -1 -1
    echo $curr_timestamp > last_timestamp.txt
  fi

   # store the current timestamp in a file for next comparison 
}

# ensures windows of class chromium are the only active windows, if there are no active windows start a chromium window
function chromium_only_check() {
    ACTIVE_WINDOW=$(xdotool getactivewindow)
    WM_CLASS=$(xprop -id $ACTIVE_WINDOW WM_CLASS 2>/dev/null)

    if [ $? -eq 0 ]; then   # check if xprop succeeded
        if [[ $WM_CLASS != *"chromium-browser"* ]] && [[ $WM_CLASS != "" ]]; then
            xdotool windowclose $ACTIVE_WINDOW
            echo "closed $ACTIVE_WINDOW with window class $WM_CLASS"
        fi
    else
        echo "No active window"
        PID_CHROME=$(pgrep -x "chromium-browse")
        if [[ -z "$PID_CHROME" ]]; then
            start_chromium
        fi
    fi
}

if [[ $1 =~ -h|--help ]]; then
    help
    exit 0
fi

# should also source $STARTUPDIR/generate_container_user
if [ -s $HOME/.bashrc ]; then
    source $HOME/.bashrc
fi

# add `--skip` to startup args, to skip the VNC startup procedure
if [[ $1 =~ -s|--skip ]]; then
    echo -e "\n\n------------------ SKIP VNC STARTUP -----------------"
    echo -e "\n\n------------------ EXECUTE COMMAND ------------------"
    echo "Executing command: '${@:2}'"
    exec "${@:2}"
fi
if [[ $1 =~ -d|--debug ]]; then
    echo -e "\n\n------------------ DEBUG VNC STARTUP -----------------"
    export DEBUG=true
fi

trap cleanup SIGINT SIGTERM

vnc_setup
browser_start
vnc_startup

## log connect options
echo -e "\n\n------------------ VNC environment started ------------------"
echo -e "\nVNCSERVER started on DISPLAY= $DISPLAY \n\t=> connect via VNC viewer with $VNC_IP:$VNC_PORT"
echo -e "\nnoVNC HTML client started:\n\t=> connect via http://$VNC_IP:$NO_VNC_PORT/?password=...\n"

if [[ $DEBUG == true ]] || [[ $1 =~ -t|--tail-log ]]; then
    echo -e "\n------------------ $HOME/.vnc/*$DISPLAY.log ------------------"
    # if option `-t` or `--tail-log` block the execution and tail the VNC log
    tail -f $STARTUPDIR/*.log $HOME/.vnc/*$DISPLAY.log
fi

# loop ensures a: the screensaver is not turned on, b: no program other than chromium can be opened and c: the Chromium window is always maximized
if [ -z "$1" ] || [[ $1 =~ -w|--wait ]]; then
    curr_timestamp=$(date +%s) # get current time in seconds
    echo $curr_timestamp > last_timestamp.txt
    while true; do   
        set +x
        sleep 0.5
        #keeps the screensaver inactive
        check_time_difference
        #ensures that chromium is the only active window
        chromium_only_check
        #ensures chrome window is always maximized
        window_maximize_check
    done
    set -x
    wait $PID_SUB
else
    # unknown option ==> call command
    echo -e "\n\n------------------ EXECUTE COMMAND ------------------"
    echo "Executing command: '$@'"
    exec "$@"
fi
