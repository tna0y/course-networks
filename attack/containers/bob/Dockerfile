FROM nginx:latest

RUN apt update && apt install -y net-tools watch tcpdump

COPY ./html /usr/share/nginx/html
COPY ./server.conf /etc/nginx/conf.d/default.conf

