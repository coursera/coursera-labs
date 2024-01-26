FROM openkbs/jdk-mvn-py3-vnc

# [Re]set env variables
ENV USER=coder
ENV HOME=/home/${USER}
ENV ECLIPSE_WORKSPACE=${HOME}/coursera/eclipse-workspace
ENV NO_VNC_HOME=${HOME}/noVNC
ENV INST_SCRIPTS=${HOME}/install
ENV WORKSPACE=${HOME}/workspace
ENV DATA=${HOME}/data

USER root
RUN usermod -l coder developer \
    && groupmod -n coder developer \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd \
    && sed -i 's/developer/coder/g' /etc/passwd \
    && mkdir -p $HOME \
    && chown $USER:$USER $HOME
USER $USER

# Download Eclipse
ENV ECLIPSE_VERSION="2022-12"
ARG ECLIPSE_TYPE="jee"
ARG ECLIPSE_RELEASE="R"
ARG ECLIPSE_OS_BUILD="linux-gtk-x86_64"
ARG ECLIPSE_MIRROR="https://download.eclipse.org"

# tar name: eclipse-jee-2022-09-R-linux-gtk-x86_64.tar.gz
ARG ECLIPSE_TAR="eclipse-${ECLIPSE_TYPE}-${ECLIPSE_VERSION}-${ECLIPSE_RELEASE}-${ECLIPSE_OS_BUILD}.tar.gz"
ARG ECLIPSE_DOWNLOAD_ROUTE="technology/epp/downloads/release/${ECLIPSE_VERSION}/${ECLIPSE_RELEASE}"
ARG ECLIPSE_DOWNLOAD_URL="${ECLIPSE_MIRROR}/${ECLIPSE_DOWNLOAD_ROUTE}"

#intermittent failures
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
    && sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4EB27DB2A3B88B8B \
    && sudo apt-get update \
    && sudo apt-get install bsdtar -y
USER root

#Install VSCode
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list \
    && apt-get install -y apt-transport-https \
    && apt-get update \
    && apt-get install -y code \
    && rm -f microsoft.gpg

USER $USER

WORKDIR /opt

# Install Chromium
RUN sudo apt-get update && sudo apt-get install -y chromium-browser

# Install Eclipse
RUN sudo wget -cq ${ECLIPSE_DOWNLOAD_URL}/${ECLIPSE_TAR} && \
    sudo tar xf ${ECLIPSE_TAR} --no-same-owner && \
    sudo rm ${ECLIPSE_TAR}

COPY eclipse.ini /opt/eclipse/eclipse.ini

RUN mkdir -p ${HOME}/.eclipse ${ECLIPSE_WORKSPACE} && \
    sudo chown -R ${USER}:${USER} ${HOME} ${HOME}/.eclipse ${ECLIPSE_WORKSPACE}

# Download IntelliJ
ARG INTELLIJ_MIRROR="https://download.jetbrains.com/idea"
ARG INTELLIJ_TAR="ideaIC-2022.3.2.tar.gz"
RUN sudo wget -cq ${INTELLIJ_MIRROR}/${INTELLIJ_TAR} \
    && sudo mkdir -p /opt/intelliJ \
    && sudo tar xf ${INTELLIJ_TAR} -C intelliJ --strip-components 1 --no-same-owner \
    && sudo rm ${INTELLIJ_TAR}

# Install Wireshark
# this bypasses the interactive element needed in the install process
RUN echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections \
    && sudo add-apt-repository ppa:wireshark-dev/stable -y \
    && sudo apt update \
    && sudo apt install -y wireshark

# Add coder to the group to be able to run wireshark
RUN sudo usermod -a -G wireshark $USER \
    && sudo setcap cap_net_admin,cap_net_raw=ep /usr/bin/dumpcap

# Allow for easier customization of filesystem, especially under mount point
COPY vnc_startup.sh /dockerstartup/vnc_startup.sh
COPY coursera-start.sh /dockerstartup/coursera-start.sh

# Run chmod separately from COPY because Coursera docker does not support it
RUN sudo chmod 777 /dockerstartup/vnc_startup.sh \
    && sudo chmod 777 /dockerstartup/coursera-start.sh

# Explicitly start window manager
# xfce4-session initializes the entire linux desktop session, so we want to 
# explicitly add in a call to start the window manager just before it to make
# sure a window manager is running.
RUN sudo sed -i 's/^\s*xfce4-session/    xfwm4\n    xfce4-session/g' /etc/xdg/xfce4/xinitrc

# Get manpages
COPY excludes /etc/dpkg/dpkg.cfg.d/excludes
RUN sudo apt install -y \
    manpages-posix

#################################
### VNC ####
#################################
WORKDIR ${HOME}

USER ${USER}

ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]

# Coursera Setup
RUN cp -r /home/developer/* /home/coder/ \
    && cp -r /home/developer/.[!.w]* /home/coder/

RUN mkdir -p ${HOME}/vscode/projects

COPY --chown=${USER}:${USER} vnc_lite.html ${HOME}/noVNC/
COPY --chown=${USER}:${USER} ui.js ${HOME}/noVNC/app
COPY --chown=${USER}:${USER} vnc.html ${HOME}/noVNC/
RUN ln -sf ${HOME}/noVNC/vnc.html ${HOME}/noVNC/index.html

# Configure Chromium to be the default browser
RUN sudo update-alternatives --set x-www-browser /usr/bin/chromium-browser
COPY chromium_config.init /home/coder/.chromium-browser.init

# For local M1+ Mac testing
# RUN mkdir -p ~/.config/Code/User/ && echo '{"extensions.verifySignature": false}' > ~/.config/Code/User/settings.json

COPY --chown=${USER}:${USER} desktop-apps/ ${HOME}/Desktop/
RUN rm ${HOME}/Desktop/Google-Chrome.desktop \
    && rm ${HOME}/Desktop/Firefox.desktop \
    && chmod 755 ${HOME}/Desktop/Chromium.desktop ${HOME}/Desktop/VSCode.desktop ${HOME}/Desktop/Eclipse.desktop ${HOME}/Desktop/IntelliJ.desktop ${HOME}/Desktop/Wireshark.desktop

# Remove sudo access from coder
RUN sudo gpasswd -d coder sudo
