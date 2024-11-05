FROM ubuntu:22.04

RUN apt update && apt install -y curl iproute2 dnsutils inetutils-ping net-tools tcpdump

COPY ./entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]
