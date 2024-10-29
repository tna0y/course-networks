#!/bin/bash

# Configure eth1
sudo ip addr add 10.0.2.2/24 dev eth1
sudo ip link set eth1 up

# Add route to reach VM A via VM B
sudo ip route add 10.0.1.0/24 via 10.0.2.1

