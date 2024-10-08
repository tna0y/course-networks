# PCAPs

This directory contains packet capture files of injections seen in the Bad Traffic Citizen Lab report.

## adhose-trickle-riseupvpn.pcap

A test from [RiseUp VPN](https://riseup.net/en/vpn) against an infrastructure IP in Egypt. We sent two requests, the first with host header "copticpope.org" and the second with host header "babylon-x.com." Both requests triggered AdHose trickle mode injections.

## egypt-packetlogic-ttl-localization.pcap

A test from [RiseUp VPN](https://riseup.net/en/vpn) against an infrastructure IP in Egypt. We sent a request with host header "copticpope.org", including a TTL-limited FIN/ACK packet for various TTL values. This helped us localize at which hop the DPI device involved in AdHose was seeing the FIN/ACK and tearing down its local connection state. We then sent a TTL-limited request with host header "aljazeera.net", which is a website known to be blocked in Egypt. This allowed us to verify that censorship was happening at the same hop (and likely at the same device) as AdHose.

## turkey-malware-injection.pcap

A test from [DigitalOcean](https://www.digitalocean.com/) against IP addresses we observed to be targeted in four provinces in Turkey. We requested a variety of targeted files from each IP, resulting in spyware injection.