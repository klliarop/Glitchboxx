#!/bin/bash

echo "=== Starting reset_environment.sh ==="
echo "Cleaning Logs directory..."
rm -rf /home/Smith_bot/Logs/*
mkdir -p /home/Smith_bot/Logs

echo "Restoring shell.c..."
cp -v /persistent_files/shell.c /home/Smith_bot/Logs/shell.c

echo "Setting permissions..."
chown -R Smith_bot:Smith_bot /home/Smith_bot
chmod 644 /home/Smith_bot/Logs/shell.c

echo "Ensuring nano directory exists..."
mkdir -p /home/Smith_bot/.local/share/nano/
chown -R Smith_bot:Smith_bot /home/Smith_bot/.local
chmod -R u+w /home/Smith_bot/

echo "Verifying contents:"
ls -la /home/Smith_bot/Logs/

echo "Starting SSH server..."
exec /usr/sbin/sshd -D