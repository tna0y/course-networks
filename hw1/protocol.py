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
        self.magic_sep = b'annndruha'
        self.sn_sep = bytes('/', encoding="UTF-8")
        self.data = data
        self.data_len = len(data)
        if self.data_len % self.window_size != 0:
            self.total_parts = self.data_len // self.window_size + 1
        else:
            self.total_parts = self.data_len // self.window_size

    def __getitem__(self, i):
        part = bytearray()
        part.extend(bytes(str(i+1), encoding="UTF-8"))
        part.extend(self.sn_sep)
        part.extend(bytes(str(self.total_parts), encoding="UTF-8"))
        part.extend(self.magic_sep)
        part.extend(self.data[i*self.window_size:(i+1)*self.window_size])
        return part

    def __iter__(self):
        for i in range(self.total_parts):
            # print(self[i])
            yield self[i]



class DeBufferizer:
    def __init__(self) -> None:
        self.window_size = 10
        self.magic_seq = b'annndruha'
        self.sn_sep = bytes('/', encoding="UTF-8")
        self.data_arr = {}
        self.total_parts = None

    def add_part(self, unknown_part):
        meta, _, part_data = unknown_part.partition(self.magic_seq)

        sequence_number, _, total_parts = meta.partition(self.sn_sep)
        if self.total_parts is None:
            self.total_parts = int(total_parts)
        else:
            assert self.total_parts == int(total_parts)
        
        self.data_arr[int(sequence_number)] = part_data

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    # def get_one_lost(self):


    def get_data(self):
        data = bytearray()
        for i in range(1, self.total_parts+1):
            data.extend(self.data_arr[i])
        return bytes(data)


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        self.max_size = 2 ** 16
        super().__init__(*args, **kwargs)

    def send(self, data: bytes):
        # print(f'send len {len(data)}')
        b = Bufferizer(data)
        for data_part in b:
            send_bytes = self.sendto(data_part)
        return len(data)

    def recv(self, n: int):
        # print(f'recv len {n}')
        d = DeBufferizer()
        while not d.is_done():
            data_part = self.recvfrom(self.max_size)
            d.add_part(data_part)
        return d.get_data()


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    run_echo_test(iterations=1, msg_size=5153)
    # b = Bufferizer(b'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')
    # d = DeBufferizer()
    # print('init ', d.is_done())
    # for part in b:
    #     d.add_part(part)
    #     print(d.is_done())
    # print(d.get_data())