#!/bin/bash
set -e

echo "[*] Resetting VPN and Docker-related iptables rules..."

VPN_NET="10.9.0.0/24"
WG_IFACE="wg0"
DOCKER_NETS=("172.18.0.0/16" "172.28.0.0/16" "172.29.0.0/16")
DOCKER_GATEWAYS=("172.28.0.1" "172.29.0.1")

echo "[*] Ensuring DOCKER-USER chain exists..."
iptables -N DOCKER-USER 2>/dev/null || true

echo "[*] Flushing DOCKER-USER chain..."
iptables -F DOCKER-USER 2>/dev/null || true

# Delete wg0-related rules from FORWARD (reverse order by line number)
echo "[*] Removing wg0-related rules from FORWARD chain..."
while iptables -L FORWARD --line-numbers -n | grep -q "$WG_IFACE"; do
    LINE=$(iptables -L FORWARD --line-numbers -n | grep "$WG_IFACE" | tail -n1 | awk '{print $1}')
    iptables -D FORWARD $LINE
done

# Remove INPUT DROP rules to Docker gateways
for GW in "${DOCKER_GATEWAYS[@]}"; do
    echo "[*] Removing INPUT/PREROUTING DROP rules to $GW..."
    iptables -D INPUT -i $WG_IFACE -d $GW -j DROP 2>/dev/null || true
    iptables -t raw -D PREROUTING -i $WG_IFACE -d $GW -j DROP 2>/dev/null || true
done

# Remove NAT POSTROUTING rules for VPN → Docker networks
for NET in "${DOCKER_NETS[@]}"; do
    echo "[*] Removing NAT POSTROUTING rules for $NET..."
    iptables -t nat -D POSTROUTING -s $VPN_NET -d $NET -j MASQUERADE 2>/dev/null || true
done

echo "[✓] Firewall reset complete — Docker and wg0-specific rules cleared."

# Show current rule summaries
echo
echo "[*] Remaining DOCKER-USER rules:"
iptables -L DOCKER-USER -n --line-numbers

echo
echo "[*] Remaining FORWARD rules:"
iptables -L FORWARD -n --line-numbers

