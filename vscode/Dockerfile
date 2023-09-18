FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NGINX_FILES_PATH=/home/nginx

# Common sdk or packages required to install languages
RUN apt-get update && apt-get install --no-install-recommends -y \
    gpg \
    curl \
    wget \
    lsb-release \
    add-apt-key \
    ca-certificates \
    dumb-init \
    git \
    sudo \
    build-essential \
    ucommon-utils \
    zip \
    unzip \
    openssh-server \
    # Python SDK
    python3 \
    python3-dev \
    python3-pip \
    # Java 11 SDK
    default-jre-headless \
    default-jdk-headless \
    maven \
    gradle \ 
    # Scala SDK
    scala \
    # C and C++ SDK
    valgrind \
    gdb \
    # C# SDK
    # mono-complete \
    # Ruby SDK
    ruby-full \
    # PHP SDK
    php \ 
    # Code Server
    libarchive-tools \
    locales \
    # Web Server
    nginx \
    supervisor \
    && apt-get clean

# Node SDK
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/nodesource.gpg \
    && echo "deb https://deb.nodesource.com/node_18.x $(lsb_release -cs) main" > /etc/apt/sources.list.d/nodesource.list \
    && echo "deb-src https://deb.nodesource.com/node_18.x $(lsb_release -cs) main" >> /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y nodejs \
    && npm install -g typescript

# Yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install --no-install-recommends yarn

# Golang SDK
ENV GO_VERSION="1.17.13"
RUN curl -sL https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz | tar -xz -C /usr/local

# Make Python3 default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Python SDK
RUN python3 -m pip install --upgrade setuptools \
    && python3 -m pip install wheel pylint requests

# Scala SDK
RUN apt-get remove scala-library scala -y \
    && wget -q http://scala-lang.org/files/archive/scala-2.13.1.deb \
    && dpkg -i scala-2.13.1.deb

# SBT
RUN echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list \
    && echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee /etc/apt/sources.list.d/sbt_old.list \
    && curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add \
    && apt-get update \
    && apt-get install sbt --no-install-recommends -y

# Rust SDK (note, this requires build-essential to exist)
ENV RUSTUP_HOME "/bin/rustup"
ENV CARGO_HOME "/bin/cargo"
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y

# Chromium SDK -- required for the old browser preview extension
RUN curl -sLO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# Code-Server
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
ENV DISABLE_TELEMETRY true

# actual install of code server
ENV CODE_VERSION="4.16.1"
RUN curl -fsSL https://code-server.dev/install.sh | bash /dev/stdin --version $CODE_VERSION

# Set up User
RUN groupadd -r coder \
    && useradd -m -r coder -g coder -s /bin/bash \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd
USER coder

# Install conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p /home/coder/miniconda
ENV PATH "${PATH}:/home/coder/miniconda/bin"

# Set up User Go Environment
RUN mkdir /home/coder/go
ENV GOPATH "/home/coder/go"
ENV PATH "${PATH}:/usr/local/go/bin:/home/coder/go/bin"

# Set up User Visual Studio Code Extensions
ENV VSCODE_USER "/home/coder/.local/share/code-server/User"
ENV VSCODE_EXTENSIONS "/home/coder/.local/share/code-server/extensions"

RUN mkdir -p ${VSCODE_USER}

# Install golang github packages
RUN go get \
    # autocompletion daemon for golang
    github.com/mdempsky/gocode \ 
    # tool to get a list of available and importable Go packages
    github.com/uudashr/gopkgs/cmd/gopkgs@v2.0 \ 
    # a tool to extract JSON representation of declarations from Go source file
    github.com/ramya-rao-a/go-outline \ 
    # a tool to extract JSON representation of package symbols from Go source tree
    github.com/acroca/go-symbols \
    # debugger for golang
    github.com/go-delve/delve/cmd/dlv \ 
    # autocompletion daemon for golang
    github.com/stamblerre/gocode \ 
    # tool to print location of the definition of a symbol
    github.com/rogpeppe/godef \ 
    # tool to add zero-value returns to incomplete Go return statements
    github.com/sqs/goreturns

# Install official golang tools
RUN go install \
    # a tool for answering questions about Go source code
    golang.org/x/tools/cmd/guru@v0.1.12 \ 
    # tool to perform precise type-safe renaming of identifiers
    golang.org/x/tools/cmd/gorename@v0.1.12

# Install golang language server separately due to package version differences
RUN go install golang.org/x/tools/gopls@v0.9.1

# Install golang linter separately due to package version differences
RUN go install golang.org/x/lint/golint@v0.0.0-20210508222113-6edffad5e616

# Set up environment variables required for Scala to work (without cosmetic errors)
RUN echo 'export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::")' >> /home/coder/.bashrc
RUN echo "export TERM=xterm" >> /home/coder/.bashrc

COPY extensions/ /tmp/
# Set up C/C++ Extension: coder-server downloads the wrong binary https://github.com/cdr/code-server/issues/2120
RUN curl -# -L -o /tmp/cpptools-linux.vsix "https://github.com/microsoft/vscode-cpptools/releases/download/1.5.1/cpptools-linux.vsix" \
    && code-server --install-extension /tmp/cpptools-linux.vsix

# Set up C# Extension (disabled since it's always trying to install packages)
#RUN code-server --install-extension ms-dotnettools.csharp --extensions-dir=$VSCODE_EXTENSIONS

# Set up Rust alias
RUN cat /usr/bin/cargo/env >> /home/coder/.bash_aliases

# code-server v3.12.0 does not use the open VSX marketplace by default. This fixes that
ENV SERVICE_URL=https://open-vsx.org/vscode/gallery 
ENV ITEM_URL=https://open-vsx.org/vscode/item

# Set up Code Runner
RUN code-server --install-extension formulahendry.code-runner --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Java Extension
    && code-server --install-extension redhat.java --extensions-dir=$VSCODE_EXTENSIONS \ 
    && code-server --install-extension vscjava.vscode-java-debug --extensions-dir=$VSCODE_EXTENSIONS \
    # Lock in this version to maintain documented testing UI
    && code-server --install-extension vscjava.vscode-java-test@0.30.1 --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension vscjava.vscode-maven --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Scala Extension
    && code-server --install-extension scala-lang.scala --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension scalameta.metals --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Go Extension
    && code-server --install-extension golang.go --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Python Extension
    && code-server --install-extension ms-python.python@2021.10.1317843341 --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up HTML/CSS Extension
    && code-server --install-extension ecmel.vscode-html-css --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Ruby Extension
    && code-server --install-extension rebornix.Ruby --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Rust Extension
    && code-server --install-extension rust-lang.rust --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up JavaScript/Node Extensions
    && code-server --install-extension xabikos.JavaScriptSnippets --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension ms-vscode.node-debug2 --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension esbenp.prettier-vscode \
    # Set up Vue.js Tooling
    && code-server --install-extension octref.vetur --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up PHP Extension
    && code-server --install-extension bmewburn.vscode-intelephense-client --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up Chrome Extension
    && code-server --install-extension msjsdiag.debugger-for-chrome --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension ritwickdey.liveServer --extensions-dir=$VSCODE_EXTENSIONS \
    # Set up React Extensions
    && code-server --install-extension dsznajder.es7-react-js-snippets --extensions-dir=$VSCODE_EXTENSIONS \
    && code-server --install-extension dbaeumer.vscode-eslint --extensions-dir=$VSCODE_EXTENSIONS

# Set up Chrome Viewer (can't be found on the code-server marketplace currently as of 07/20/2020)
# We don't want to download the vsix file here because it fails too often.
RUN mkdir -p $VSCODE_EXTENSIONS/vscode-browser-preview \
    && bsdtar --strip-components=1 -xf /tmp/auchenberg.vscode-browser-preview-0.6.7.vsix -C $VSCODE_EXTENSIONS/vscode-browser-preview extension

# Set up coursera launch button extension
RUN mkdir -p $VSCODE_EXTENSIONS/coursera-launch-button \
    && bsdtar --strip-components=1 -xf /tmp/coursera-launch-button-0.0.1.vsix -C $VSCODE_EXTENSIONS/coursera-launch-button extension

# This fixes the health check bug
COPY index.html /home/travis/build/codercom/code-server/packages/server/build/web/

# Remove extra notifications
RUN find $VSCODE_EXTENSIONS -wholename "*ritwickdey.liveserver*/out/src/announcement/index.js" \
    | xargs sed -i --expression='/showInformationMessage/d'

ENV SHELL /bin/bash

USER root

# Launch button
COPY --chown=coder:coder coursera-launch-button/ $VSCODE_USER/coursera/
COPY --chown=coder:coder launchButtonSettings.json /tmp/launchButtonSettings.json
RUN mkdir -p /home/coder/coursera

# Turns off the welcome page
COPY --chown=coder:coder settings.json $VSCODE_USER

# Makes terminal open bash by default
COPY start.sh /usr/local/bin/
COPY config.yaml /tmp/config/code-server/
RUN chmod 755 /usr/local/bin/start.sh

# Put coursera submission scripts in python lib
COPY coursera-submission /tmp/coursera
RUN for d in $(ls /usr/lib | grep "^python*") ; do cp -r /tmp/coursera /usr/lib/$d; done

# Web server
VOLUME ["/etc/nginx/sites-enabled", "/etc/nginx/certs", "/etc/nginx/conf.d", "/var/log/nginx", "/var/www/html"]
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directory for nginx-related files
RUN mkdir -p $NGINX_FILES_PATH
COPY nginx-files/ /tmp/nginx-files/

USER coder

# Create supervisord log files
RUN mkdir -p /var/log/supervisor
RUN sudo touch /var/log/supervisor/supervisord.log \
  && sudo touch /var/log/supervisor/code-server-stdout.log \
  && sudo touch /var/log/supervisor/code-server-stderr.log
RUN sudo chmod 766 /var/log/supervisor/*

# Setup User Workspace
RUN mkdir -p /home/coder/project

# Copy the default .hidden file
COPY .hidden /tmp/.hidden

# Create a template reverse-proxy for partners to modify if they wish
COPY nginx-files/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf.template

# Setting up directory for global npm packages (installed via easy docker config)
RUN sudo mkdir -p /home/npm-global
WORKDIR /home/npm-global
RUN sudo npm init -y

# Set global npm prefix (packages installed here still get symlinked to the project directory)
# under /home/coder/project, so unfortunately they will still be under mount point
RUN sudo npm config set prefix /home/npm-global --global
RUN sudo chown coder:coder /home/npm-global

WORKDIR /home/coder/project

ENTRYPOINT ["dumb-init", "--"]

USER root
CMD ["start.sh"]

# This will generally always be needed for React apps
RUN npm install react-scripts --global \
    # Needed for reverse-proxy easy config
    && npm install nginx-conf --global  
