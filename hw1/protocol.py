import socket
import json
import base64
import random


class UDPBasedProtocol:
    def __init__(self, *, local_addr, remote_addr):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.remote_addr = remote_addr
        self.udp_socket.bind(local_addr)

    def sendto(self, data):
        return self.udp_socket.sendto(data, self.remote_addr)

    def recvfrom(self, n):
        msg, addr = self.udp_socket.recvfrom(n)
        return msg


class Packet:
    def __init__(self, data: bytes) -> None:
        self.N = 256
        self.id = None
        self.data = data

    def serialize(self):
        self.id = random.randbytes(self.N)
        packet_data = bytearray()
        packet_data.extend(self.id)
        packet_data.extend(self.data)
        return packet_data

    def load(self, packet_data: bytes):
        self.id = packet_data[:self.N]
        self.data = bytes(packet_data[self.N:])
        return self.data


class MyTCPProtocol(UDPBasedProtocol):  # Ограничение UDP пакета 65к байт
    def __init__(self, *args, **kwargs):
        self.buffer_size = 2 ** 16
        super().__init__(*args, **kwargs)
        self.seen_ids = set()

    def send(self, data: bytes):  # Отправлять произвольную длину
        packet = Packet(data)
        packet_data = packet.serialize()
        for i in range(5):
            send_bytes = self.sendto(packet_data)
            assert send_bytes == len(packet_data)
        return len(data)

    def recv(self, n: int):  # n - макимальная длиная получаемых данных
        while True:
            packet_data = self.recvfrom(self.buffer_size)
            packet = Packet(b'')
            packet.load(packet_data)
            if packet.id not in self.seen_ids:
                self.seen_ids.add(packet.id)
                return packet.data


if __name__ == "__main__":
    data = b'777dsgsdgsdgsdgsdgsdgs334943'
    print('Send', data)
    p = Packet(data)
    packet_data = p.serialize()
    print('Transfer', packet_data)
    recv = Packet(b'').load(packet_data)
    print('Recv', recv)

# Запускать доп потоки на отправку и получение пакетов
# буферы получения, буферы отправки
# send и read будут заниматься тем что будут писать в буферы и читать оттуда
