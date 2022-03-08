#!/usr/bin/env bash
mkdir -p /home/coder/project/.dotfiles-coursera
git config --global core.fileMode false

# initialize npm inside home directory
cd /home/coder/
npm init -y

# copy .hidden and .readonly files to /home/nginx/
cp -n /tmp/nginx-files/.hidden /home/nginx/
cp -n /tmp/nginx-files/.readonly /home/nginx/

# copy reverse-proxy default template into /home/nginx/ only if it doesn't exist
if [ ! -f /home/nginx/reverse-proxy.conf ]; then
    cp /etc/nginx/sites-enabled/reverse-proxy.conf.template /home/nginx/reverse-proxy.conf
    chmod a+w /home/nginx/reverse-proxy.conf
fi

# link reverse-proxy from mount point to location where it actually takes effect
ln -s /home/nginx/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf
export PATH=/home/npm-global/bin:$PATH

/usr/bin/supervisord
