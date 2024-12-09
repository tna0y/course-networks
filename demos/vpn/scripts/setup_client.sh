#!/bin/bash
set -xeuo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

TUN_NAME="tun0"
TUN_IP="10.0.0.2"
TUN_NETWORK="10.0.0.0/24"
SERVER_TUN_IP="10.0.0.1"
SERVER_PUBLIC_IP="x.x.x.x"

ip addr add ${TUN_IP}/24 dev ${TUN_NAME}
ip link set ${TUN_NAME} up

DEFAULT_ROUTE=$(ip route show default | awk '/default/ {print $3}')
echo "Saving current default gateway: ${DEFAULT_ROUTE}"

ip route add ${SERVER_PUBLIC_IP}/32 via ${DEFAULT_ROUTE}

# Change default gateway to go through VPN
ip route del default
ip route add default via ${SERVER_TUN_IP}

echo "Client VPN network configuration completed" 