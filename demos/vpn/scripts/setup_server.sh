#!/bin/bash
set -xeuo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

TUN_NAME="tun0"
TUN_IP="10.0.0.1"
TUN_NETWORK="10.0.0.0/24"

ip addr add ${TUN_IP}/24 dev ${TUN_NAME}
ip link set ${TUN_NAME} up

echo 1 > /proc/sys/net/ipv4/ip_forward

MAIN_INTERFACE=$(ip route get 8.8.8.8 | awk '{print $5; exit}')

iptables -t nat -A POSTROUTING -s ${TUN_NETWORK} -o ${MAIN_INTERFACE} -j MASQUERADE

iptables -A FORWARD -i ${TUN_NAME} -o ${MAIN_INTERFACE} -j ACCEPT
iptables -A FORWARD -i ${MAIN_INTERFACE} -o ${TUN_NAME} -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "Server VPN network configuration completed" 