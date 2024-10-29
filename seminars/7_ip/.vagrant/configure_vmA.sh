#!/bin/bash

# Configure eth1
INTERFACE="enp0s9"

sudo ip addr add 10.0.1.1/24 dev $INTERFACE
sudo ip link set $INTERFACE up

# Add route to reach VM C via VM B
sudo ip route add 10.0.2.0/24 via 10.0.1.2
