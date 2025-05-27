#!/bin/bash
set -e

echo "[+] Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

VPN_NET="10.9.0.0/24"
DOCKER_NET1="172.18.0.0/16"
DOCKER_NET2="172.28.0.0/16"
DOCKER_NET3="172.29.0.0/16"
HOST_IFACE="wg0"
DOCKER_GATEWAY_1="172.28.0.1"
DOCKER_GATEWAY_2="172.29.0.1"

echo "[+] Blocking VPN inter-usaer traffic..."
iptables -C FORWARD -i $HOST_IFACE -s $VPN_NET -d $VPN_NET -j DROP 2>/dev/null || \
iptables -A FORWARD -i $HOST_IFACE -s $VPN_NET -d $VPN_NET -j DROP

echo "[+] Dropping VPN → Docker network traffic by default..."
for net in $DOCKER_NET1 $DOCKER_NET2 $DOCKER_NET3; do
    iptables -C DOCKER-USER -i $HOST_IFACE -s $VPN_NET -d $net -j DROP 2>/dev/null || \
    iptables -A DOCKER-USER -i $HOST_IFACE -s $VPN_NET -d $net -j DROP

    iptables -C DOCKER-USER -i $HOST_IFACE -s $net -d $net -j DROP 2>/dev/null || \
    iptables -A DOCKER-USER -i $HOST_IFACE -s $net -d $net -j DROP

    echo "[+] Enabling return traffic NAT for VPN → $net..."
    iptables -t nat -C POSTROUTING -s $VPN_NET -d $net -j MASQUERADE 2>/dev/null || \
    iptables -t nat -A POSTROUTING -s $VPN_NET -d $net -j MASQUERADE
done

echo "[+] Blocking VPN access to published Docker services at $DOCKER_GATEWAY_1..."
iptables -C INPUT -i $HOST_IFACE -d $DOCKER_GATEWAY_1 -j DROP 2>/dev/null || \
iptables -A INPUT -i $HOST_IFACE -d $DOCKER_GATEWAY_1 -j DROP

# Optional (redundant in many cases but catches pre-DNAT traffic)
iptables -t raw -C PREROUTING -i $HOST_IFACE -d $DOCKER_GATEWAY_1 -j DROP 2>/dev/null || \
iptables -t raw -A PREROUTING -i $HOST_IFACE -d $DOCKER_GATEWAY_1 -j DROP


echo "[+] Blocking VPN access to published Docker services at $DOCKER_GATEWAY_2..."
iptables -C INPUT -i $HOST_IFACE -d $DOCKER_GATEWAY_2 -j DROP 2>/dev/null || \
iptables -A INPUT -i $HOST_IFACE -d $DOCKER_GATEWAY_2 -j DROP

# Optional (redundant in many cases but catches pre-DNAT traffic)
iptables -t raw -C PREROUTING -i $HOST_IFACE -d $DOCKER_GATEWAY_2 -j DROP 2>/dev/null || \
iptables -t raw -A PREROUTING -i $HOST_IFACE -d $DOCKER_GATEWAY_2 -j DROP


echo "[+] Base firewall rules configured."
echo "[*] Use dynamic rules in Python to allow specific container IPs per user."
