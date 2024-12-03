
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


# GRE

![Alt text](image-4.png)

R1
```sh
ip route 192.168.2.0 255.255.255.0 10.0.0.2


interface Tunnel0

    ip address 10.0.0.1 255.255.255.0

    tunnel source 1.1.2.1

    tunnel destination 1.2.3.3
```

R3
```sh
ip route 192.168.1.0 255.255.255.0 10.0.0.1

interface Tunnel0

    ip address 10.0.0.2 255.255.255.0

    tunnel source 1.2.3.3

    tunnel destination 1.1.2.1
```


# ACL
```sh
# Просмотр текущих ACL
show access-lists

# Создание стандартного ACL
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any

# Применение стандартного ACL к интерфейсу (входящий трафик)
interface FastEthernet0/0
 ip access-group 10 in

# Создание расширенного ACL
access-list 101 permit tcp 192.168.1.0 0.0.0.255 any eq 80
access-list 101 deny ip any any

# Применение расширенного ACL к интерфейсу (исходящий трафик)
interface FastEthernet0/0
 ip access-group 101 out

# Удаление ACL
no access-list 10


# Дебаг и диагностика
debug ip access-list
```

# IPSec

![Alt text](image-5.png)

В отлчиче от GRE нам важно существование маршрута до stub подсетей. Это нужно из-за того, что шифрование применяется как самый последний шаг после отправки пакета, после маршрутизации.

Также как и в прошлом примере предполагаем существование маршрута между R1 и R3.
```sh
# Текущие сессии шифрования
sh crypto session
# активные SA
sh crypto isakmp sa
```

R1
```sh

# Политики будут перебираться по номеру, начиная с 1. Наша политика простая: просто использовать пароль
crypto isakmp policy 1
 authentication pre-share

# Для соседа 1.2.3.3 зададим пароль "cisco"
crypto isakmp key cisco address 1.2.3.3

# Перечислим доступные алгортмы шифрования
crypto ipsec transform-set AES128-SHA esp-aes esp-sha-hmac

# crypto map MAP1 - настройки конкретного тоннеля
crypto map MAP1 10 ipsec-isakmp
 set peer 1.2.3.3
 set transform-set AES128-SHA
 # применять только к пакетам, соответствующим access-list'у 101
 match address 101

interface FastEthernet0/0
 ip address 1.1.2.1 255.255.255.0
 # Применяем шифрование для пакетов, проходящих через этот интерфейс
 crypto map MAP1

# access-list, с помощью которого мы выбираем какие пакеты шифровать
access-list 101 permit ip 192.168.1.0 0.0.0.255 192.168.2.0 0.0.0.255

# Очень важно. Пакет должн быть маршрутизируемым еще до инкапсуляции.
ip route 192.168.2.0 255.255.255.0 1.2.3.3

```

R3
```sh

# Политики будут перебираться по номеру, начиная с 1. Наша политика простая: просто использовать пароль
crypto isakmp policy 1
 authentication pre-share

# Для соседа 1.1.2.1 зададим пароль "cisco"
crypto isakmp key cisco address 1.1.2.1

# Перечислим доступные алгортмы шифрования
crypto ipsec transform-set AES128-SHA esp-aes esp-sha-hmac

# crypto map MAP1 - настройки конкретного тоннеля
crypto map MAP1 10 ipsec-isakmp
 set peer 1.1.2.1
 set transform-set AES128-SHA
 # применять только к пакетам, соответствующим access-list'у 101
 match address 101

interface FastEthernet0/0
 ip address 1.2.3.3 255.255.255.0
 # Применяем шифрование для пакетов, проходящих через этот интерфейс
 crypto map MAP1

# access-list, с помощью которого мы выбираем какие пакеты шифровать
access-list 101 permit ip 192.168.2.0 0.0.0.255 192.168.1.0 0.0.0.255

# Очень важно. Пакет должн быть маршрутизируемым еще до инкапсуляции.
ip route 192.168.1.0 255.255.255.0 1.1.2.2

```
