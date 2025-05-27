#!/bin/bash

# Clean logs
rm -rf /home/${SSH_USERNAME}/Logs/*

# Restore original shell.c
cp /opt/template_shell.c /home/${SSH_USERNAME}/Logs/shell.c

# Fix ownership and permissions
chown -R ${SSH_USERNAME}:${SSH_USERNAME} /home/${SSH_USERNAME}
chmod 644 /home/${SSH_USERNAME}/Logs/shell.c

# Restore root files if needed
[ -f /root/Super_Reality_Override.exe ] || echo "BOUHAHA!" > /root/Super_Reality_Override.exe
[ -f /root/READ_ME ] || echo "Important" > /root/READ_ME

# Start SSH
exec /usr/sbin/sshd -D -e

