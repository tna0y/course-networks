#!/bin/bash

# Configure eth1 (to VM A)



sudo ip addr add 10.0.1.2/24 dev eth1
sudo ip link set eth1 up

# Configure eth2 (to VM C)
sudo ip addr add 10.0.2.1/24 dev eth2
sudo ip link set eth2 up

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Make IP forwarding persistent across reboots
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Set up NAT (masquerading) for traffic from VM A to VM C
sudo iptables -t nat -A POSTROUTING -o eth2 -s 10.0.1.0/24 -j MASQUERADE

# Save iptables rules to make them persistent
sudo apt-get update
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save