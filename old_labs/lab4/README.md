# Лабораторная 4: OSPF + BGP



![Alt text](image-0.png)
![Alt text](image-1.png)


# OSPF

```bash
# Информация о всех узлах OSPF
show ip ospf database

# Информация о собственных stub сегментах
show ip ospf database self-originate

# Аналогично RIP, операционная информация
show ip protocols

# Информация о соседях
show ip ospf neighbor

# Визуализация маршрутов
show ip ospf rib

# Показать маршруты, построенные с помощью OSPF
show ip route ospf
```
Конфигурация для построения OSPF на схеме из роутеров ниже.
![Alt text](image-5.png)
R1
```bash
interface FastEthernet0/0
    ip address 1.0.1.1 255.255.255.0
    no shutdown

interface FastEthernet2/0
    ip address 1.1.4.1 255.255.255.0
    no shutdown

router ospf 1
    log-adjacency-changes
    router-id 1.1.1.1
    network 1.1.4.0 0.0.0.255 area 1
    network 1.0.1.0 0.0.0.255 area 1
```

R2
```bash
interface FastEthernet0/0
    ip address 1.0.2.1 255.255.255.0
    no shutdown

interface FastEthernet1/0
    ip address 1.2.3.2 255.255.255.0
    no shutdown

interface FastEthernet2/0
    ip address 1.1.4.2 255.255.255.0
    no shutdown

router ospf 1
    log-adjacency-changes
    router-id 2.2.2.2
    network 1.0.2.0 0.0.0.255 area 1
    network 1.1.4.0 0.0.0.255 area 1
    network 1.2.3.0 0.0.0.255 area 1
```

R3
```bash
interface FastEthernet0/0
    ip address 1.0.3.1 255.255.255.0
    no shutdown

interface FastEthernet1/0
    ip address 1.2.3.3 255.255.255.0
    no shutdown

router ospf 1
    router-id 3.3.3.3
    log-adjacency-changes
    network 1.0.3.0 0.0.0.255 area 1
    network 1.2.3.0 0.0.0.255 area 1
```
R4
```bash

interface Loopback0
    ip address 1.0.4.1 255.255.255.255
    no shutdown
interface FastEthernet2/0
    ip address 1.1.4.4 255.255.255.0
    no shutdown

router ospf 1
    log-adjacency-changes
    network 1.0.4.1 0.0.0.0 area 1
    network 1.1.4.0 0.0.0.255 area 1
```


дополнительно
```bash
router ospf <n>
    # изменить базовую пропускную способность 
    auto-cost reference-bandwidth 100000

```

# BGP
```shell

# информация о базе данных с bgp маршрутами
show ip bgp
# включить дебаг сообщения об изменениях состояния bgp соединений
debug bgp all

```
Конфигурация роутера
```shell
# настройка роутера с AS 10
router bgp 10
  # подключенная к BGP сеть 
  network 192.168.12.0
  network 192.168.13.0
  # явное задание соседа и его AS
  neighbor 192.168.13.3 remote-as 10
  # опциональное задание веса соседа (больше - приоритетнее)
  neighbor 192.168.13.3 weight 100
  # рекламировать подключенные сети в BGP. Что еще можно рекламировать?
  redistribute connected
  # отключаем классы
  no auto-summary


```