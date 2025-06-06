#!/bin/bash

echo "=== Starting reset_environment.sh ==="
echo "Cleaning Logs directory..."
rm -rf /home/Smith_bot/Logs/*  # Remove all files in the Logs directory for the SSH user
mkdir -p /home/Smith_bot/Logs  # Ensure the Logs directory exists

echo "Restoring shell.c..."
cp -v /persistent_files/shell.c /home/Smith_bot/Logs/shell.c  # Copy shell.c from persistent storage to Logs

echo "Setting permissions..."
chown -R Smith_bot:Smith_bot /home/Smith_bot  # Set ownership of home directory to the SSH user
chmod 644 /home/Smith_bot/Logs/shell.c  # Set permissions for shell.c

echo "Ensuring nano directory exists..."
mkdir -p /home/Smith_bot/.local/share/nano/  # Ensure nano config directory exists
chown -R Smith_bot:Smith_bot /home/Smith_bot/.local  # Set ownership for .local directory
chmod -R u+w /home/Smith_bot/  # Ensure user has write permissions in home directory

echo "Verifying contents:"
ls -la /home/Smith_bot/Logs/  # List contents of Logs directory for verification

echo "Starting SSH server..."
exec /usr/sbin/sshd -D  # Start the SSH server in the foreground