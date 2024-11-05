# Семинар 8: iptables
## 1: фильтрация пакетов
```bash
# Заблокировать все ICMP (ping) запросы от A к C
sudo iptables -A FORWARD -s 172.1.2.1 -d 172.2.3.3 -p icmp -j DROP

# Разрешить ping только в определенное время (например, с 9:00 до 17:00)
sudo iptables -A FORWARD -s 172.1.2.1 -d 172.2.3.3 -p icmp -m time --timestart 09:00 --timestop 17:00 -j ACCEPT
```
## 2: SNAT
```bash
# Настроить SNAT на ВМ B для трафика от ВМ A к C
sudo iptables -t nat -A POSTROUTING -s 172.1.2.1 -o enp0s9 -j SNAT --to-source 172.2.3.2
```

## 3: port forwarding и DNAT   
```bash

# Установить nginx на ВМ C (выполните на ВМ C)
sudo apt update && sudo apt install -y nginx

# На ВМ B перенаправить HTTP-трафик на ВМ C
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -d 172.1.2.2 -j DNAT --to-destination 172.2.3.3:80
sudo iptables -A FORWARD -p tcp -d 172.2.3.3 --dport 80 -j ACCEPT
```

## 4: firewall и state
```bash
# Разрешить новые SSH-подключения от ВМ A к C
sudo iptables -A FORWARD -p tcp --dport 22 -s 172.1.2.1 -d 172.2.3.3 -m state --state NEW -j ACCEPT

# Разрешить установленные и связанные подключения в обоих направлениях
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# Заблокировать новые SSH-подключения от ВМ C к A
sudo iptables -A FORWARD -p tcp --dport 22 -s 172.2.3.3 -d 172.1.2.1 -j DROP
```

## 5: Логирование трафика
```bash
# Логировать все отброшенные пакеты от ВМ A к ВМ C
sudo iptables -A FORWARD -s 172.1.2.1 -d 172.2.3.3 -j LOG --log-prefix "DROP_LOG: " --log-level 4

# Логировать только TCP-трафик на порту 80 от ВМ A к ВМ C
sudo iptables -A FORWARD -p tcp --dport 80 -s 172.1.2.1 -d 172.2.3.3 -j LOG --log-prefix "HTTP_LOG: " --log-level 4
```

## 6: ratelimit
```bash
# Ограничить SSH-подключения от ВМ A к C до 2 подключений в минуту
sudo iptables -A FORWARD -p tcp --dport 22 -s 172.1.2.1 -d 172.2.3.3 -m limit --limit 2/min --limit-burst 3 -j ACCEPT
sudo iptables -A FORWARD -p tcp --dport 22 -s 172.1.2.1 -d 172.2.3.3 -j DROP
```

## 7: netfilter queue
```bash
# Добавить правило NFQUEUE на ВМ B для TCP-трафика на порту 80
sudo iptables -A FORWARD -p tcp --dport 80 -j NFQUEUE --queue-num 1
```

main.py
```python
from scapy.all import *
from netfilterqueue import NetfilterQueue

def process_packet(packet):
    scapy_packet = IP(packet.get_payload())
    if scapy_packet.haslayer(Raw) and b"old_string" in scapy_packet[Raw].load:
        scapy_packet[Raw].load = scapy_packet[Raw].load.replace(b"old_string", b"new_string")
        del scapy_packet[IP].chksum
        del scapy_packet[TCP].chksum
        packet.set_payload(bytes(scapy_packet))
    packet.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, process_packet)
try:
    print("Waiting for packets...")
    nfqueue.run()
except KeyboardInterrupt:
    print("\nStopping...")
nfqueue.unbind()
```
```bash
sudo apt install python3-scapy python3-netfilterqueue
sudo python3 main.py
```