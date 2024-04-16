FROM 268845366347.dkr.ecr.us-east-1.amazonaws.com/base/linux-base:latest

USER $USER

## ============================ ECLIPSE =================================
# Download
ENV ECLIPSE_VERSION="2022-12"
ARG ECLIPSE_TYPE="jee"
ARG ECLIPSE_RELEASE="R"
ARG ECLIPSE_OS_BUILD="linux-gtk-x86_64"
ARG ECLIPSE_MIRROR="https://download.eclipse.org"

# tar name: eclipse-jee-2022-09-R-linux-gtk-x86_64.tar.gz
ARG ECLIPSE_TAR="eclipse-${ECLIPSE_TYPE}-${ECLIPSE_VERSION}-${ECLIPSE_RELEASE}-${ECLIPSE_OS_BUILD}.tar.gz"
ARG ECLIPSE_DOWNLOAD_ROUTE="technology/epp/downloads/release/${ECLIPSE_VERSION}/${ECLIPSE_RELEASE}"
ARG ECLIPSE_DOWNLOAD_URL="${ECLIPSE_MIRROR}/${ECLIPSE_DOWNLOAD_ROUTE}"

USER root
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --import - \
    && sudo apt-get update

WORKDIR /opt

# Install
RUN sudo wget -cq ${ECLIPSE_DOWNLOAD_URL}/${ECLIPSE_TAR} && \
    sudo tar xf ${ECLIPSE_TAR} --no-same-owner && \
    sudo rm ${ECLIPSE_TAR}

COPY eclipse.ini /opt/eclipse/eclipse.ini

RUN mkdir -p ${HOME}/.eclipse ${ECLIPSE_WORKSPACE} && \
    sudo chown -R ${USER}:${USER} ${HOME} ${HOME}/.eclipse ${ECLIPSE_WORKSPACE}

## ============================ INTELLIJ =============================
# Download and install
ARG INTELLIJ_MIRROR="https://download.jetbrains.com/idea"
ARG INTELLIJ_TAR="ideaIC-2022.3.2.tar.gz"
RUN sudo wget -cq ${INTELLIJ_MIRROR}/${INTELLIJ_TAR} \
    && sudo mkdir -p /opt/intelliJ \
    && sudo tar xf ${INTELLIJ_TAR} -C intelliJ --strip-components 1 --no-same-owner \
    && sudo rm ${INTELLIJ_TAR}

## ============================ WIRESHARK ============================
# Install Wireshark
# this bypasses the interactive element needed in the install process
RUN echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections \
    && sudo add-apt-repository ppa:wireshark-dev/stable -y \
    && sudo apt update \
    && sudo apt install -y wireshark

# Add coder to the group to be able to run wireshark
RUN sudo usermod -a -G wireshark $USER \
    && sudo setcap cap_net_admin,cap_net_raw=ep /usr/bin/dumpcap

## ============================ VSCODE ==========================
# Install 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list \
    && apt-get install -y apt-transport-https \
    && apt-get update \
    && apt-get install -y code \
    && rm -f microsoft.gpg

## ============================ CHROMIUM =======================
# Get debian repos for chromium
COPY debian.list /etc/apt/sources.list.d/debian.list
RUN sudo gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys DCC9EFBF77E11517 \
    && sudo gpg --export 77E11517 | sudo gpg --dearmour -o /usr/share/keyrings/debian-buster.gpg 
RUN sudo gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 648ACFD622F3D138 \
    && sudo gpg --export 22F3D138 | sudo gpg --dearmour -o /usr/share/keyrings/debian-buster-updates.gpg 
RUN sudo gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 112695A0E562B32A \
    && sudo gpg --export E562B32A | sudo gpg --dearmour -o /usr/share/keyrings/debian-security-buster.gpg
COPY chromium.pref /etc/apt/preferences.d/chromium.pref

# Install chromium from debian repo
RUN sudo apt update \
    && sudo apt install -y chromium

# Allow for easier customization of filesystem, especially under mount point
COPY coursera-start.sh /dockerstartup/coursera-start.sh

# Run chmod separately from COPY because Coursera docker does not support it
RUN sudo chmod 777 /dockerstartup/coursera-start.sh

# Explicitly start window manager
# xfce4-session initializes the entire linux desktop session, so we want to 
# explicitly add in a call to start the window manager just before it to make
# sure a window manager is running.
# RUN sudo sed -i 's/^\s*xfce4-session/    xfwm4\n    xfce4-session/g' /etc/xdg/xfce4/xinitrc

#################################
### VNC ####
#################################
WORKDIR ${HOME}

USER ${USER}

ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]

COPY --chown=${USER}:${USER} desktop-apps/ ${HOME}/Desktop/

# For local M1+ Mac testing
# RUN mkdir -p ~/.config/Code/User/ && echo '{"extensions.verifySignature": false}' > ~/.config/Code/User/settings.json

# Create desktop icons
COPY --chown=${USER}:${USER} desktop-apps/ ${HOME}/Desktop/
RUN chmod 755 ${HOME}/Desktop/Chromium.desktop ${HOME}/Desktop/VSCode.desktop ${HOME}/Desktop/Eclipse.desktop ${HOME}/Desktop/IntelliJ.desktop ${HOME}/Desktop/Wireshark.desktop
