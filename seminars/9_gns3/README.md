# Установка и первичная настройка GNS3

GNS3 состоит из двух компонентов: GNS3 GUI и GNS3 Server. Интерфейс работает на локальной машине, а сервер может быть установлен как локально, так и на удалённой машине.

Сервер требует Linux окружения с некоторыми зависимостями. Для этого сервер рекомендуется запускать в специально виртуальной машине (GNS3 VM). Можно использовать как VirtualBox, так и VMware. При желании можно также запустить сервер на практически любом Linux хосте. 

## Ссылки

- **GNS3**: [https://github.com/GNS3/gns3-gui/releases/tag/v2.2.51](https://github.com/GNS3/gns3-gui/releases/tag/v2.2.51)
- **GNS3 VM**: [https://github.com/GNS3/gns3-gui/releases/tag/v2.2.51](https://github.com/GNS3/gns3-gui/releases/tag/v2.2.51)

Версии сервера (VM) и десктопного приложения должны совпадать. Например, GNS3.VM.VirtualBox.2.2.51.zip для GNS3 v2.2.51.

## Видео установки и настройки GNS3

- **Под Windows с использованием VirtualBox**: [Видеоинструкция](https://www.youtube.com/watch?v=rC5yVrSa7-U&list=PLHVUfYYv0xkkWgyC962qJsEISPmUhq0aB&index=23)
- **Под Mac с ARM с использованием VMware**: [Видеоинструкция в записи от 30.03](https://drive.google.com/drive/folders/1tIYZECWyk3lb8QuLyPqUZmWRBcgGDNJJ)

### VirtualBox (рекомендуется в большинстве случаев)

- Установить VirtualBox + Extension Pack: [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)

### VMware Workstation (Windows/Linux) / Fusion (Mac) — для устройств на ARM

- **VMware Fusion**: [https://customerconnect.vmware.com/evalcenter?p=fusion-player-personal-13](https://customerconnect.vmware.com/evalcenter?p=fusion-player-personal-13)
- **VMware Workstation**: [https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html](https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html)

### Установка GNS3 Server на свой удалённый сервер

Если ваш ноутбук слабее 2 ядер / 4 ГБ RAM, рассмотрите установку GNS3 Server на удалённый сервер:

- [https://github.com/GNS3/gns3-server/blob/master/README.md](https://github.com/GNS3/gns3-server/blob/master/README.md)


---

## Настройка и установка устройства в GNS3

Для работы будем использовать платформу Cisco C3725. Это роутер, но в него можно установить слот расширения NM-16ESW, который добавит 16 L2 портов. После этого его можно использовать как свитч.

### Скачивание образа

- Скачайте образ по ссылке: [https://mega.nz/folder/nJR3BTjJ#N5wZsncqDkdKyFQLELU1wQ/file/WYRGxRiL](https://mega.nz/folder/nJR3BTjJ#N5wZsncqDkdKyFQLELU1wQ/file/WYRGxRiL)
- Название файла: `c3725-adventerprisek9-mz124-15.bin`

### Установка образа в GNS3

1. **Добавление образа в GNS3**

   - В меню выберите `Edit` → `Preferences` → `Dynamips` → `IOS routers` → `New` → `New Image`.
   - Выберите скачанный файл образа и далее соглашайтесь со всеми настройками по умолчанию.

2. **Добавление модуля расширения**

   - В окне **Network Adapters** добавьте карточку **NM-16ESW** в слот 1.

     ![Network Adapters](image-1.png)

3. **Настройка Idle PC**

   - В окне **Idle PC** нажмите на кнопку **Idle-PC Finder** и дождитесь, пока найдётся значение.
   - Если после нескольких попыток значение не найдено, можно пропустить этот шаг.

---

## Полезные команды

### Общие команды

```shell
# Показать полную информацию обо всех интерфейсах
show interfaces

# Краткая информация об интерфейсах
show ip interface brief

# Войти в режим конфигурации
configure terminal

# Показать текущую конфигурацию
show running-config

# Сохранить текущую конфигурацию
write

# Исследовать опции команды при помощи "?"
show ?

# Автодополнение команды клавишей Tab
sh<tab>
# Результат:
show
```

### Работа с интерфейсами

```shell
# Войти в настройки интерфейса F2/0 (в режиме конфигурации)
interface F2/0

# Настроить несколько интерфейсов одновременно
interface range F2/1 - 2
```

---

## Настройка LAG (Link Aggregation Group)

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
```

---

## Создание первой сети в GNS3

В этом разделе мы создадим простую сеть, состоящую из двух компьютеров (PC1 и PC2), соединённых через свитч SW1 на базе установленного ранее Cisco C3725 с модулем NM-16ESW.

### Шаги по созданию сети

1. **Запуск GNS3**

   - Откройте GNS3 и создайте новый проект (`File` → `New Blank Project`).
   - Дайте проекту понятное имя, например, `First_Network`.

2. **Добавление устройств**

   - В левом меню найдите раздел **End Devices**.
   - Перетащите два устройства типа **VPCS** (Virtual PC Simulator) на рабочее поле. Они будут обозначены как PC1 и PC2.
   - В разделе **Routers** найдите ранее установленный образ Cisco C3725.
   - Перетащите его на рабочее поле; это будет наш свитч SW1.

3. **Переименование устройств**

   - Для удобства переименуйте устройства:
     - Щёлкните правой кнопкой мыши на каждом устройстве и выберите **Change hostname**.
     - Переименуйте их соответственно: `PC1`, `PC2`, `SW1`.

4. **Соединение устройств**

   - Выберите инструмент соединения (иконка с кабелем или **Add a link**).
   - Соедините **PC1** с **SW1**:
     - Нажмите на `PC1`, выберите интерфейс `Ethernet0`.
     - Нажмите на `SW1`, выберите интерфейс `FastEthernet2/0`.
   - Соедините **PC2** с **SW1**:
     - Нажмите на `PC2`, выберите интерфейс `Ethernet0`.
     - Нажмите на `SW1`, выберите интерфейс `FastEthernet2/1`.

5. **Настройка SW1**

   - Запустите устройство `SW1` (щёлкните правой кнопкой мыши и выберите **Start**).
   - Откройте консоль `SW1` (щёлкните правой кнопкой мыши и выберите **Console**).
   - Выполните следующие команды для базовой настройки:

     ```shell
     # Войти в привилегированный режим
     enable
     # Войти в режим конфигурации
     configure terminal

     # Перевести интерфейсы в активное состояние
     interface range FastEthernet2/0 - 1
       no shutdown
     exit

     # Сохранить конфигурацию
     write
     ```

6. **Настройка PC1 и PC2**

   - Откройте консоль `PC1` (двойным щелчком по иконке).
   - Назначьте IP-адрес:

     ```shell
     # Назначить IP-адрес 192.168.1.1 с маской 255.255.255.0
     ip 192.168.1.1 255.255.255.0
     ```

   - Повторите те же действия для `PC2`, но с другим IP-адресом:

     ```shell
     # Назначить IP-адрес 192.168.1.2 с маской 255.255.255.0
     ip 192.168.1.2 255.255.255.0
     ```

7. **Проверка связи**

   - На `PC1` выполните команду:

     ```shell
     # Пинг до PC2
     ping 192.168.1.2
     ```

   - Вы должны увидеть успешные ответы, что означает, что сеть настроена правильно.

### Дополнительные настройки (опционально)

- **Проверка MAC-адресов на SW1**

  - В консоли `SW1` выполните команду:

    ```shell
    # Показать таблицу MAC-адресов
    show mac address-table
    ```

- **Просмотр состояния интерфейсов**

  - В консоли `SW1` выполните команду:

    ```shell
    # Показать состояние интерфейсов
    show interfaces status
    ```
