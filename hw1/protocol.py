import socket
import json
import base64
import os
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



class Bufferizer:
    def __init__(self, data: bytes) -> None:
        self.window_size = 10
        self.magic_seq = b'annndruha'
        self.data = data
        self.data_len = len(data)
        if self.data_len % self.window_size != 0:
            self.total_parts = self.data_len // self.window_size + 1
        else:
            self.total_parts = self.data_len // self.window_size
        print(self.total_parts)

    def __getitem__(self, i):
        part = bytearray()
        part.extend(bytes(str(i+1), encoding="UTF-8"))
        part.extend(bytes('/', encoding="UTF-8"))
        part.extend(bytes(str(self.total_parts), encoding="UTF-8"))
        part.extend(self.magic_seq)
        part.extend(self.data[i*self.window_size:(i+1)*self.window_size])
        return part



class DeBufferizer:
    def __init__(self) -> None:
        pass




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
        # self.seen_ids = set()

    def send(self, data: bytes):  # Отправлять произвольную длину
        print(f'send len {len(data)}')
        packet = Packet(data)
        packet_data = packet.serialize()
        # for i in range(5):
        send_bytes = self.sendto(packet_data)
        # assert send_bytes == len(packet_data)
        return len(data)

    def recv(self, n: int):  # n - макимальная длиная получаемых данных
        # while True:
        print(f'recv len {n}')
        packet_data = self.recvfrom(self.buffer_size)
        packet = Packet(b'')
        packet.load(packet_data)
            # if packet.id not in self.seen_ids:
                # self.seen_ids.add(packet.id)
        return packet.data


if __name__ == "__main__":
    # from protocol_test import setup_netem, run_echo_test
    # setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    # run_echo_test(iterations=1, msg_size=5153)
    b = Bufferizer(b'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')
    for i in range(b.total_parts):
        print(b[i])