#!/bin/env bash
sleep 1

tcpdump -i eth0 -U -w /data/alice.pcap &
sleep 3

while true ; do 
    curl -L -i -o - http://10.0.1.3/public.html | head -n 20
    sleep 10
done
