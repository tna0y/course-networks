# Генерация и использование x509 сертификатов с помощью OpenSSL с использованием SAN

## 1. Генерация CA сертификата

Создать корневой сертификат центра сертификации (CA):

```bash
# Создание приватного ключа CA
openssl genrsa -out ca.key 4096

# Создание самоподписанного сертификата CA
openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.pem -subj "/C=RU/ST=State/L=City/O=Organization/OU=Org/CN=MyCA"

# Вывод содержимого сертификата CA
openssl x509 -in ca.pem -text -noout
```

## 2. Создание CSR с использованием SAN

### Создайте конфигурационный файл для CSR

Создайте файл `server.cnf` со следующим содержимым:

```ini
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = req_ext

[dn]
C  = RU
ST = State
L  = City
O  = Organization
OU = Org
CN = localhost

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
```

### Создайте приватный ключ и CSR

```bash
# Создание приватного ключа сервера
openssl genrsa -out server.key 2048

# Создание CSR с использованием конфигурационного файла
openssl req -new -key server.key -out server.csr -config server.cnf

# Вывод содержимого CSR
openssl req -in server.csr -text -noout
```

## 3. Выпуск подписанного сертификата с SAN

Создайте файл расширений `v3.ext`:

```ini
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
```

Подпишите CSR с использованием CA и файла расширений:

```bash
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.crt -days 500 -sha256 -extfile v3.ext

# Вывод содержимого подписанного сертификата
openssl x509 -in server.crt -text -noout
```
## Установка сертификата и запуск сервера


```bash
docker compose up
```

Откройте `https://localhost` или `https://127.0.0.1` в браузере для проверки.

## Полезное
* [OpenSSL Cheat Sheet 🔐](https://gist.github.com/Hakky54/b30418b25215ad7d18f978bc0b448d81)

## mitmproxy
Демонстрация на семинаре