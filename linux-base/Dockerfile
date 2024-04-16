FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

#### ---------------------
#### ---- USER, GROUP ----
#### ---------------------
ENV USER_ID=1000
ENV GROUP_ID=1000

##############################################
#### ---- Installation Directories   ---- ####
##############################################
ENV SCRIPT_DIR=/usr/scripts

###########################################
#### ---- System: certificates : ---- #####
#### ---- Corporate Proxy      : ---- #####
###########################################
ENV LANG C.UTF-8
ARG LIB_BASIC_LIST="curl wget unzip ca-certificates"
RUN set -eux; \
    apt-get update -y && \
    apt-get install -y ${LIB_BASIC_LIST} 
    
COPY setup-scripts/ ${SCRIPT_DIR}
RUN chmod -R 755 ${SCRIPT_DIR}
RUN mkdir -p /certificates
RUN ${SCRIPT_DIR}/setup_system_certificates.sh
RUN ${SCRIPT_DIR}/setup_system_proxy.sh

########################################
#### update ubuntu and Install Python 3
########################################
ARG LIB_DEV_LIST="apt-utils automake pkg-config libpcre3-dev zlib1g-dev liblzma-dev"
ARG LIB_BASIC_LIST="curl iputils-ping nmap net-tools build-essential software-properties-common apt-transport-https"
ARG LIB_COMMON_LIST="bzip2 libbz2-dev git wget unzip vim python3-pip python3-setuptools python3-dev python3-venv python3-numpy python3-scipy python3-pandas python3-matplotlib python-is-python3"
ARG LIB_TOOL_LIST="graphviz libsqlite3-dev sqlite3 git xz-utils"

RUN apt-get update -y && \
    apt-get install -y ${LIB_DEV_LIST} && \
    apt-get install -y ${LIB_BASIC_LIST} && \
    apt-get install -y ${LIB_COMMON_LIST} && \
    apt-get install -y ${LIB_TOOL_LIST} && \
    apt-get install -y sudo && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

########################################
#### ------- OpenJDK Installation ------
########################################
ENV JAVA_VERSION=17

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

# A few reasons for installing distribution-provided OpenJDK:
#
#  1. Oracle.  Licensing prevents us from redistributing the official JDK.
#
#  2. Compiling OpenJDK also requires the JDK to be installed, and it gets
#     really hairy.
#
#     For some sample build times, see Debian's buildd logs:
#       https://buildd.debian.org/status/logs.php?pkg=openjdk-8

RUN apt-get update && apt-get install -y --no-install-recommends \
		bzip2 \
		unzip \
		xz-utils \
	&& rm -rf /var/lib/apt/lists/*

# Default to UTF-8 file.encoding
ENV LANG C.UTF-8

ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

RUN set -ex && \
	mkdir -p /usr/share/man/man1 && \
	apt-get update && \
	apt-get install -y --no-install-recommends openjdk-${JAVA_VERSION}-jdk && \
	rm -rf /var/lib/apt/lists/* && \
# update-alternatives so that future installs of other OpenJDK versions don't change /usr/bin/java
	update-alternatives --get-selections | awk -v home="$(readlink -f "$JAVA_HOME")" 'index($3, home) == 1 { $2 = "manual"; print | "update-alternatives --set-selections" }'; \
# ... and verify that it actually worked for one of the alternatives we care about
	update-alternatives --query java | grep -q 'Status: manual'

########################################
#### ---- PIP install packages ---- ####
########################################
COPY requirements.txt ./

# pip3 uninstall pkg-resources==0.0.0
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip --no-cache-dir install --ignore-installed -U -r requirements.txt

## -- added Local PIP installation bin to PATH
ENV PATH=${PATH}:${HOME}/.local/bin

## VERSIONS ##
ENV PATH=${PATH}:${JAVA_HOME}/bin

# RUN mvn --version && \
RUN python3 -V && \
    pip3 --version

#########################################
#### ---- Node from NODESOURCES ---- ####
#########################################
RUN set -uex && \
    apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
     | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    NODE_MAJOR=18 && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
     > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y && \
    npm install -g npm@latest
    
RUN cd ${SCRIPT_DIR}; ${SCRIPT_DIR}/setup_npm_proxy.sh

########################
#### ---- Yarn ---- ####
########################
# Ref: https://classic.yarnpkg.com/en/docs/install/#debian-stable
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update -y && \ 
    apt-get install -y yarn

###################################
#### ------ user: coder ------ ####
###################################
ENV USER=coder
ENV HOME=/home/${USER}

## -- setup NodeJS user profile
RUN groupadd ${USER} && useradd ${USER} -m -d ${HOME} -s /bin/bash -g ${USER} && \
    ## -- Ubuntu -- \
    usermod -aG sudo ${USER} && \
    echo "${USER} ALL=NOPASSWD:ALL" | tee -a /etc/sudoers && \
    echo "USER =======> ${USER}" && ls -al ${HOME}

############################################
#### ---- Set up user environments ---- ####
############################################
ENV WORKSPACE=${HOME}/workspace
ENV DATA=${HOME}/data

WORKDIR ${HOME}

# ############################################
# #### ---- Volumes: data, workspace ---- ####
# ############################################
RUN mkdir -p ${WORKSPACE} ${DATA}
RUN chown ${USER}:${USER} -R  ${DATA}

VOLUME ${DATA}
VOLUME ${WORKSPACE}

############################################
#### ---- NPM: websocket           ---- ####
############################################
RUN npm install websocket ws

#### --------------------------------------------------
#### ---- Connection ports for controlling the UI: ----
#### --------------------------------------------------
ENV DISPLAY=${DISPLAY:-":1"}

ENV VNC_PORT=${VNC_PORT:-"5901"}
ENV NO_VNC_PORT=${NO_VNC_PORT:-"6901"}

EXPOSE ${VNC_PORT}
EXPOSE ${NO_VNC_PORT}

#### ---------------------------------------
#### ---- Window Manager: xfce or icewm ----
#### ---------------------------------------
ENV WINDOW_MANAGER=xfce

##################################
#### ---- VNC / noVNC ----    ####
##################################

ENV TERM=xterm \
    STARTUPDIR=/dockerstartup \
    INST_SCRIPTS=${HOME}/install \
    NO_VNC_HOME=${HOME}/noVNC \
    VNC_COL_DEPTH=24 \
    VNC_VIEW_ONLY=false

#### -----------------------------------------------------------------
#### ---- VNC Resolution (1280x1024, 1600x1024, 1920x1280, etc.): ----
#### -----------------------------------------------------------------
ENV VNC_RESOLUTION=${VNC_RESOLUTION:-1920x1080}

### Add all install scripts for further steps
COPY install-scripts/ ${INST_SCRIPTS}/
RUN find ${INST_SCRIPTS} -name '*.sh' -exec chmod a+x {} +

### Install some common tools
RUN ${INST_SCRIPTS}/tools.sh
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

### Install xvnc-server & noVNC - HTML5 based VNC viewer
RUN ${INST_SCRIPTS}/tigervnc.sh
RUN ${INST_SCRIPTS}/no_vnc.sh

### Install WINDOW_MANAGER (xfce or icewm) UI
RUN apt-get --fix-missing update
RUN ${INST_SCRIPTS}/${WINDOW_MANAGER}_ui.sh
ADD xfce/ ${HOME}/

### configure startup
COPY dockerstartup/ ${STARTUPDIR}
RUN ${INST_SCRIPTS}/set_user_permission.sh ${STARTUPDIR} ${HOME}

### Add manpages
COPY excludes /etc/dpkg/dpkg.cfg.d/excludes
RUN sudo apt-get install -y \
    manpages-posix \
    man \
    manpages

#### --------------------------
#### ---- XDG Open Utility ----
#### --------------------------
RUN apt-get install -y xdg-utils --fix-missing

#### -------------------------------------
#### ---- Reset Owner and Permissions ----
#### -------------------------------------
RUN chmod a+x /dockerstartup/vnc_startup.sh && \
    mkdir ${HOME}/.local && \
    chown -R ${USER}:${USER} ${HOME}

#################################################################
#### ---- Fix missing: /host/run/dbus/system_bus_socket ---- ####
#################################################################
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
ENV DBUS_SYSTEM_BUS_SOCKET=/host/run/dbus/system_bus_socket

#### ---- fixing DBUS connection issue ----
# RUN echo "Set disable_coredump false" >> /etc/sudo.conf && \
#     sudo apt-get install -y dbus-x11

RUN sudo mkdir -p ${DBUS_SYSTEM_BUS_SOCKET} && sudo chmod go+rw ${DBUS_SYSTEM_BUS_SOCKET}

### Use custom VNC html
COPY --chown=${USER}:${USER} vnc-files/ui.js ${HOME}/noVNC/app
# Default display.js, rfb.js may be okay, need to test on platform
# COPY --chown=${USER}:${USER} vnc-files/display.js ${HOME}/noVNC/core
COPY --chown=${USER}:${USER} vnc-files/rfb.js ${HOME}/noVNC/core
COPY --chown=${USER}:${USER} vnc-files/vnc.html ${HOME}/noVNC/
RUN ln -sf ${HOME}/noVNC/vnc.html ${HOME}/noVNC/index.html

#########################
#### ---- Entry ---- ####
#########################
USER $USER
WORKDIR ${HOME}
#### Define default command.
ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]
