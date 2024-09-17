# Семинар Wireshark + HTTP
## Wireshark
* 1_http.pcap - Пример работы протокола http
* 2_twitter_auth.pcap - Пример задания на анализ трафика. Найти логин и пароль пользователя.
* 3_http_with_jpegs.pcap - Запись трафика, содержащая изображения. Какое животное изображено на одном из изображений?
* live capture demo
* http://34.170.67.1/ - Определить версию сервера nginx

## tcpdump
```# tcpdump -i any -U -s0 -w - 'not port 22' | wireshark -k -i -```

