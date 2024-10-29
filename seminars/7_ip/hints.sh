

apt install net-tools iproute2

netstat -rn



ssh 34.41.84.229 sudo tcpdump -i ens4  -w - -U port not 22 | /Applications/Wireshark.app/Contents/MacOS/Wireshark -k -i -



ip link set dev {INTERFACE} {down / up}
ip a add {IP/MASK} dev {INTERFACE}
ip a add 192.168.1.200/24 dev eth0
ip addr add broadcast {IP} dev {INTERFACE}
ip addr add broadcast 172.20.10.255 dev dummy0

ip neigh show
ip neigh add {IP} lladdr {MAC/LLADDRESS} dev {DEVICE} nud {STATE}
ip neigh add 192.168.1.5 lladdr 00:1a:30:38:a8:00 dev eth0 nud perm
ip neigh del {IP} dev {DEVICE}
ip neigh del 192.168.1.5 dev eth1

ip route
ip route add default {NETWORK/MASK} dev {DEVICE}
ip route add default {NETWORK/MASK} via {GATEWAYIP}

ip route add {NETWORK/MASK} via {GATEWAYIP}
ip route add {NETWORK/MASK} dev {DEVICE}
ip route add default {NETWORK/MASK} dev {DEVICE}
ip route add default {NETWORK/MASK} via {GATEWAYIP}

ip link set dev {INTERFACE} down
ip link set dev {INTERFACE} address {MAC}
ip link set dev {INTERFACE} up

iptables -L INPUT


iptables -A INPUT -i lo -j ACCEPT
iptables -D INPUT 10
iptables -D INPUT -m conntrack --ctstate INVALID -j DROP

/var/log/kern.log
iptables -A INPUT -s 192.168.11.0/24 -j LOG --log-prefix='[netfilter] '


iptables -A {INPUT|OUTPUT} -p icmp -j {ACCEPT|REJECT|DROP}
iptables -A {INPUT|OUTPUT} -p icmp --icmp-type {0|8}  -j {ACCEPT|REJECT|DROP}
iptables -A {INPUT|OUTPUT} -p icmp --icmp-type {echo-reply|echo-request} -j {ACCEPT|REJECT|DROP}
iptables -A {INPUT|OUTPUT} -p icmp --icmp-type {echo-reply|echo-request} -m state --state NEW,ESTABLISHED,RELATED -j {ACCEPT|REJECT|DROP}

sysctl net.ipv4.ip_forward