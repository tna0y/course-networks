
## Настройка LAG (Link Aggregation Group) (aka Port Channel, EtherChannel) 

```shell
# Настроить LAG на интерфейсах F2/1 и F2/2
interface F2/1
  channel-group 1 mode on
  no shutdown

interface F2/2
  channel-group 1 mode on
  no shutdown
```

---

## Взаимодействие со STP (Spanning Tree Protocol)

```shell
# Посмотреть состояние STP
show spanning-tree brief

# Задать стоимость порта в интерфейсе F2/0
interface F2/0
  spanning-tree cost 100

# Задать приоритет
spanning-tree vlan 1 priority 4096

# Вывод лога событий
debug spanning-tree events
```
---

## Port Security
Не нужно в лабе, для общего развития.
```shell
# Показать таблицу привязки MAC адресов к портам
show mac address-table

Внутри интерфейса:
    # port security доступен только для access портов
    switchport mode access
    # Включить port-security на данном порту
    switchport port-security
    # Задать максимальное количество мак адресов на порту
    switchport port-security maximum 1
    # Зафиксировать адрес 00:00:00:00:00:00 на текущемпорту
    switchport port-security mac-address 00:00:00:00:00:00
    # задать sticky режим порту
    switchport port-security mac-address sticky 
    # задать действие в случае нарушения
    switchport port-security violation { shutdown | restrict | protect }
```

# VLAN 802.1q
```shell
# показать инфо по вланам
show vlan brief

# включить вланы в режиме конфигурации
vlan 2,3

# настройка access интерфейса
    switchport mode access # по умолчанию
    switchport access vlan 2

# настройка trunk интерфейса
    switchport trunk encapsulation dot1q
    switchport mode trunk
    switchport trunk allowed vlan 2,3 # опционально
```
