#!/usr/bin/env bash
python3 ${VSCODE_USER}/coursera/submitButton.py
/usr/local/bin/mysqlServer.sh mysqld &
code-server --config /tmp/config/code-server/config.yaml
