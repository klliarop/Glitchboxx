#!/bin/bash

echo "[*] Backing up current iptables rules..."
iptables-save > ~/iptables-backup-$(date +%F-%H%M%S).rules

echo "[*] Flushing all iptables rules and chains..."

# Flush all rules
iptables -F
iptables -t nat -F
iptables -t raw -F
iptables -t mangle -F

# Delete all user-defined chains
iptables -X
iptables -t nat -X
iptables -t raw -X
iptables -t mangle -X

# Set default policies to ACCEPT (safe)
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

echo "[*] Current iptables rules (should be empty except for Docker if running):"
iptables -L -v -n --line-numbers
iptables -t nat -L -v -n --line-numbers
iptables -t raw -L -v -n --line-numbers

echo "[✓] iptables reset complete."
