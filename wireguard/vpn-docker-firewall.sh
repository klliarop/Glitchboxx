#!/bin/bash

# 1. Enable IP forwarding (lets VPN talk to Docker)
echo "[+] Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

# 2. Flush old rules (optional but clean)
iptables -F
iptables -t nat -F

# 3. Allow VPN to Docker only
echo "[+] Setting firewall: VPN 10.9.0.0/24 -> Docker 172.18.0.0/16"
iptables -A FORWARD -i wg0 -d 172.18.0.0/16 -j ACCEPT
iptables -A FORWARD -o wg0 -s 172.18.0.0/16 -j ACCEPT

# 4. Drop all other VPN traffic (this protects host!)
echo "[+] Blocking VPN from touching host or other networks"
iptables -A FORWARD -i wg0 ! -d 172.18.0.0/16 -j DROP

# 5. Allow Docker response routing (NAT)
iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -d 172.18.0.0/16 -j MASQUERADE

echo "[+] Done. Your VPN clients can now reach Docker containers only."
