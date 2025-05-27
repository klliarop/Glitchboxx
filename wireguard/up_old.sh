#!/bin/bash
iptables -F
iptables -t nat -F

# Enable IP forwarding
echo "[+] Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

# Isolate VPN users from each other
echo "[+] Blocking communication between users in 10.9.0.0/24"
iptables -A FORWARD -i wg0 -s 10.9.0.0/24 -d 10.9.0.0/24 -j DROP

# Allow users to reach gateway
echo "[+] Enabling communication of users in 10.9.0.0/24 with gateway 10.9.0.1"
iptables -A FORWARD -i wg0 -s 10.9.0.0/24 -d 10.9.0.1 -j ACCEPT
iptables -A FORWARD -o wg0 -s 10.9.0.0/24 -d 10.9.0.1 -j ACCEPT

echo "[+] Setting NAT to allow docker to reply to VPN"
# NAT to Docker network (if container can't route back)
iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -d 172.18.0.10 -j MASQUERADE
