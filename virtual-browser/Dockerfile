FROM openkbs/jdk-mvn-py3-vnc

# [Re]set env variables
ENV USER=coder
ENV HOME=/home/${USER}
ENV ECLIPSE_WORKSPACE=${HOME}/coursera/eclipse-workspace
ENV NO_VNC_HOME=${HOME}/noVNC
ENV INST_SCRIPTS=${HOME}/install
ENV WORKSPACE=${HOME}/workspace
ENV DATA=${HOME}/data
ENV IMAGE_TYPE=AWS_CLOUD

#Instantiates 'coder' user
USER root
RUN usermod -l coder developer \
    && groupmod -n coder developer \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd \
    && sed -i 's/developer/coder/g' /etc/passwd \
    && mkdir -p $HOME \
    && chown $USER:$USER $HOME
USER $USER

#Public keys
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
    && sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4EB27DB2A3B88B8B 

WORKDIR /opt

#Install third party applications
RUN sudo apt-get update && \
    sudo apt-get install -y \
    bsdtar \
    zip \
    chromium-browser \
    dbus \ 
    emacs \
    openbox \ 
    wmctrl \ 
    coreutils \ 
    x11-utils \
    xdotool \
    inotify-tools\
    xdotool

# Disables the use of right click outside the browser, 
# restricting user access to the terminal and other native openbox applications
RUN mkdir -p $HOME/.config/openbox
ADD rc.xml $HOME/.config/openbox/rc.xml

COPY vnc_startup.sh /dockerstartup/vnc_startup.sh
# Run chmod separately from COPY because Coursera docker does not support it
RUN sudo chmod 777 /dockerstartup/vnc_startup.sh 

# Explicitly start window manager
# xfce4-session initializes the entire linux desktop session, so we want to 
# explicitly add in a call to start the window manager just before it to make
# sure a window manager is running.
RUN sudo sed -i 's/^\s*xfce4-session/    xfwm4\n    xfce4-session/g' /etc/xdg/xfce4/xinitrc

#User workspace setup
WORKDIR ${HOME}
USER ${USER}
ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]

# Coursera Setup
RUN cp -r /home/developer/* /home/coder/ \
    && cp -r /home/developer/.[!.w]* /home/coder/

#noVNC setup
COPY --chown=${USER}:${USER} vnc-files/ui.js ${HOME}/noVNC/app
COPY --chown=${USER}:${USER} vnc-files/display.js ${HOME}/noVNC/core
COPY --chown=${USER}:${USER} vnc-files/vnc.html ${HOME}/noVNC/
COPY --chown=${USER}:${USER} vnc-files/rfb.js ${HOME}/noVNC/core
RUN ln -sf ${HOME}/noVNC/vnc.html ${HOME}/noVNC/index.html

#Browser setup
RUN rm ${HOME}/Desktop/Google-Chrome.desktop 
COPY chromium_config.init /home/coder/.chromium-browser.init

#Policies are inspired by:
# https://github.com/webedx-spark/rhyme-app/blob/9c879916a6b2b6f811a3f92a04b75f68cdf198fa/deploy/docker/virtual-browser-turbovnc/policy.json
RUN sudo mkdir -p /etc/chromium/policies/managed/
COPY policy.json /etc/chromium/policies/managed/policies.json

#Overwriting default thunar file manager with 'thunar' script that opens files in Chromium file manager
RUN sudo mv /usr/bin/thunar /usr/bin/thunar-original
COPY thunar /usr/bin/thunar
RUN sudo chmod +x /usr/bin/thunar

# Remove sudo access from coder
RUN sudo gpasswd -d coder sudo
