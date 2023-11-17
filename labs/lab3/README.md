# Лабораторная 3: RIP

![Alt text](image-0.png)
![Alt text](image-1.png)


## Настройка оборудования

Использовать будем роутер c3725, установленный для 1й лабораторной.
Для выполнения лабы на роутере потребуется 3+ L3 портов. Добавить карты с L3 портами можно следующим образом:

1. Откройте меню настройки образа, кликнув в GNS3 правой кнопкой мышки на образ и выберите "Configure template".
![Alt text](image-2.png)
2. Во вкладке "Slots" добавьте необходимое количество карт "NM-1FE-TX".
![Alt text](image-3.png)

## RIP

```bash
# показать таблицу RIP
show ip rip database

# Таймеры и прочая информация про настройку протоколов маршрутизации, втч RIP
show ip protocols
```
Конфигурация для построения RIP на схеме из роутеров ниже.
![Alt text](image-4.png)

R1
```bash
interface FastEthernet0/0
    # адрес и маска подсети
    ip address 1.0.1.1 255.255.255.0
    # l3 интерфейсы надо явно включать
    no shutdown


interface FastEthernet0/1
    ip address 1.1.2.1 255.255.255.0
    no shutdown

router rip
    # RIPv2
    version 2
    # Уменьшаем таймеры для увеличения скорости сходимости при демонстрации лабы
    timers basic 3 18 18 24
    # Сети, в которых следует включить RIP
    network 1.1.2.0
    # рекламировать информацию о всех подключенных подсетях
    redistribute connected
    # Для RIP v1 (не обязательно тут), без этой настройки рекламируемые подсети будут "огругляться" до ближайшей классовой сети.
    no auto-summary
    # кол-во дублирующих путей 
    maximum-paths 1
```

R2
```bash
interface FastEthernet0/0
    ip address 1.0.2.1 255.255.255.0
    no shutdown


interface FastEthernet0/1
    ip address 1.1.2.2 255.255.255.0
    no shutdown

interface FastEthernet1/0
    ip address 1.2.3.2 255.255.255.0
    no shutdown

router rip
    version 2
    timers basic 3 18 18 24
    network 1.1.2.0
    network 1.2.3.0
    redistribute connected
    no auto-summary
```


R3
```bash
interface FastEthernet0/0
    ip address 1.0.3.1 255.255.255.0
    no shutdown

interface FastEthernet1/0
    ip address 1.2.3.3 255.255.255.0
    no shutdown

router rip
    version 2
    timers basic 3 18 18 24
    network 1.2.3.0
    redistribute connected
    no auto-summary
```
