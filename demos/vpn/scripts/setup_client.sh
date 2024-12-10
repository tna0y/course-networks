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
SERVER_PUBLIC_IP="192.168.56.10"

ip addr add ${TUN_IP}/24 dev ${TUN_NAME}
ip link set ${TUN_NAME} up

# Если мы находимся в разных подсетях с нашим впн сервером,
# то при отсутствии маршрута по умолчанию нам нужно явно указать, что до VPN сервера
# дорога лежит через "старый" маршрут по умолчанию.

# DEFAULT_ROUTE=$(ip route show default | awk '/default/ {print $3}')
# ip route add ${SERVER_PUBLIC_IP}/32 via ${DEFAULT_ROUTE}

ip route del default
ip route add default via ${SERVER_TUN_IP}
