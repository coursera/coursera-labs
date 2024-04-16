#!/usr/bin/env bash
set -e

echo "Install TigerVNC server"
# VERSION_TIGERVNC=${VERSION_TIGERVNC:-1.9.0}
VERSION_TIGERVNC=${VERSION_TIGERVNC:-1.10.0}
# (site not available) wget -qO- https://dl.bintray.com/tigervnc/stable/tigervnc-1.9.0.x86_64.tar.gz | tar xz --strip 1 -C /
# wget -qO- https://sourceforge.net/projects/tigervnc/files/stable/1.9.0/tigervnc-1.9.0.x86_64.tar.gz/download | tar xz --strip 1 -C /
# (Use variable)
wget -qO- https://sourceforge.net/projects/tigervnc/files/stable/${VERSION_TIGERVNC}/tigervnc-${VERSION_TIGERVNC}.x86_64.tar.gz/download | tar xz --strip 1 -C /
