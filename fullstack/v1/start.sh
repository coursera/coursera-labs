#!/usr/bin/env bash
mongod -f /etc/mongod.conf &
python3 ${VSCODE_USER}/coursera/submitButton.py
code-server --config /tmp/config/code-server/config.yaml
