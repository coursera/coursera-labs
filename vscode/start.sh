#!/usr/bin/env bash
su -c "cp -n /tmp/launchButtonSettings.json /home/coder/coursera/" - coder
python3 ${VSCODE_USER}/coursera/refreshButtonConfig.py

# git in lab persistence + default options
mkdir -p /home/coder/project/.dotfiles-coursera
git config --global core.fileMode false

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
