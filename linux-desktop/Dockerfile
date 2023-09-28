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

# downloading from http://mirror.math.princeton.edu/pub/eclipse/technology/epp/downloads/release/2022-09/R/
ARG ECLIPSE_DOWNLOAD_ROUTE="technology/epp/downloads/release/${ECLIPSE_VERSION}/${ECLIPSE_RELEASE}"
ARG ECLIPSE_DOWNLOAD_URL="${ECLIPSE_MIRROR}/${ECLIPSE_DOWNLOAD_ROUTE}"

#intermittent failures
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
    && sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4EB27DB2A3B88B8B \
    && sudo apt-get update \
    && sudo apt-get install bsdtar -y

WORKDIR /opt
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

# Copy over resources for firefox launch page
COPY firefox-launch-page/ /tmp/firefox-launch-page
COPY syspref.js /etc/firefox/
RUN sudo wget -O /tmp/Source_Sans_3.zip https://fonts.google.com/download?family=Source%20Sans%203

# Allow for easier customization of filesystem, especially under mount point
COPY vnc_startup.sh /dockerstartup/vnc_startup.sh
COPY coursera-start.sh /dockerstartup/coursera-start.sh

# Run chmod separately from COPY because Coursera docker does not support it
RUN sudo chmod 644 /tmp/firefox-launch-page/* \
    && sudo chmod 644 /etc/firefox/syspref.js \
    && sudo chmod 777 /dockerstartup/vnc_startup.sh \
    && sudo chmod 777 /dockerstartup/coursera-start.sh

RUN sudo apt update && sudo apt install -y traceroute dnsutils ettercap-common
RUN sudo apt install -y whois snmpd zip tcpdump hping3
RUN sudo apt-get install -y software-properties-common wget && sudo add-apt-repository universe 
RUN sudo wget https://packages.ntop.org/apt-stable/18.04/all/apt-ntop-stable.deb \
    && sudo apt install -y ./apt-ntop-stable.deb \
    && sudo apt-get install -y ntopng

# Explicitly start window manager
# xfce4-session initializes the entire linux desktop session, so we want to 
# explicitly add in a call to start the window manager just before it to make
# sure a window manager is running.
RUN sudo sed -i 's/^\s*xfce4-session/    xfwm4\n    xfce4-session/g' /etc/xdg/xfce4/xinitrc

#################################
### VNC ####
#################################
WORKDIR ${HOME}

USER ${USER}

ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]

# Coursera Setup
RUN cp -r /home/developer/* /home/coder/ \
    && cp -r /home/developer/.[!.w]* /home/coder/

COPY --chown=${USER}:${USER} vnc_lite.html ${HOME}/noVNC/
RUN ln -sf ${HOME}/noVNC/vnc_lite.html ${HOME}/noVNC/index.html

COPY --chown=${USER}:${USER} desktop-apps/ ${HOME}/Desktop/

RUN rm ${HOME}/Desktop/Google-Chrome.desktop \
    && chmod 755 ${HOME}/Desktop/Eclipse.desktop ${HOME}/Desktop/IntelliJ.desktop ${HOME}/Desktop/Firefox.desktop ${HOME}/Desktop/Wireshark.desktop

# Remove sudo access from coder
RUN sudo gpasswd -d coder sudo
