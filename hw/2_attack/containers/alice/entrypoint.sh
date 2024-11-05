#!/bin/env bash
sleep 1

tcpdump -i eth0 -w /data/alice.pcap &

while true ; do 
    curl -L -i -o - http://10.0.1.3/public.html | head -n 20
    sleep 10
done