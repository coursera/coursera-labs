#!/usr/bin/env bash
set -e

echo "Install Openbox"
apt-get update
apt-get install -y supervisor openbox xterm xfonts-base xauth xinit
apt-get purge -y pm-utils xscreensaver*
apt-get clean -y