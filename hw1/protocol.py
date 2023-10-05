import socket
import json
import base64


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
        self.data = data
        self.id = hash(data)

    def serialize(self):
        return json.dumps({
            'id': self.id,
            'data': base64.b64encode(self.data).decode()
        }).encode()

    @classmethod
    def load(cls, data: bytes):
        data = json.loads(data)
        packet = Packet(b'')
        packet.id = data['id']
        packet.data = base64.b64decode(data['data'].encode())
        return packet


class MyTCPProtocol(UDPBasedProtocol):  # Ограничение UDP пакета 65к байт
    def __init__(self, *args, **kwargs):
        self.buffer_size = 2 ** 24
        super().__init__(*args, **kwargs)
        self.seen_ids = set()

    def send(self, data: bytes):  # Отправлять произвольную длину
        packet = Packet(data)
        packet_data = packet.serialize()
        for i in range(2):
            send_bytes = self.sendto(packet_data)
            assert send_bytes == len(packet_data)
        return len(data)

    def recv(self, n: int):  # n - макимальная длиная получаемых данных
        while True:
            packet_data = self.recvfrom(self.buffer_size)
            packet = Packet.load(packet_data)
            if packet.id not in self.seen_ids:
                self.seen_ids.add(packet.id)
                return packet.data[:n]

# Запускать доп потоки на отправку и получение пакетов
# буферы получения, буферы отправки
# send и read будут заниматься тем что будут писать в буферы и читать оттуда
