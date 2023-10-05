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
        self.window_size = 1024
        self.magic_sep = b'annndruha'
        self.sn_sep = bytes('/', encoding="UTF-8")
        self.data = data
        self.data_len = len(data)
        self.data_id = os.urandom(48)
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
        part.extend(self.data_id)
        part.extend(self.magic_sep)
        part.extend(self.data[i*self.window_size:(i+1)*self.window_size])
        return part

    def __iter__(self):
        for i in range(self.total_parts):
            yield self[i]



class DeBufferizer:
    def __init__(self) -> None:
        self.window_size = 1024
        self.magic_seq = b'annndruha'
        self.sn_sep = bytes('/', encoding="UTF-8")
        self.data_arr = {}
        self.total_parts = None
        self.data_id = None

    def add_part(self, unknown_part):
        meta, _, part_data = unknown_part.partition(self.magic_seq)

        sequence_number, _, total_parts = meta.partition(self.sn_sep)
        if self.total_parts is None:
            self.total_parts = int(total_parts)
        else:
            assert self.total_parts == int(total_parts)

        data_id, _, part_data = part_data.partition(self.magic_seq)

        if self.data_id is None:
            self.data_id = data_id
        else:
            if self.data_id == data_id:
                self.data_arr[int(sequence_number)] = part_data

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    def get_losts(self):
        return set(range(1, self.total_parts+1)) - set(self.data_arr.keys())


    def get_data(self):
        data = bytearray()
        for i in range(1, self.total_parts+1):
            data.extend(self.data_arr[i])
        return bytes(data)


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        self.max_size = 2 ** 32
        super().__init__(*args, **kwargs)

    def send(self, data: bytes):
        b = Bufferizer(data)
        for data_part in b:
            self.sendto(data_part)
            print("========SEND:", bytes(data_part))
        # self.sendto(data)
        # print("========SEND============", bytes(data))
        return len(data)

    def recv(self, n: int):
        d = DeBufferizer()
        while not d.is_done():
            data_part = self.recvfrom(self.max_size)
            print("========RECV:", bytes(data_part))
            d.add_part(data_part)
        return d.get_data()
        # data = self.recvfrom(self.max_size)
        # print("========RECV============", bytes(data))
        # return data


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    # msg_size = 10_000_000
    # setup_netem(packet_loss=0.00, duplicate=0.00, reorder=0.00)
    # run_echo_test(iterations=2, msg_size=msg_size)


    setup_netem(packet_loss=0.0, duplicate=0.1, reorder=0.0)
    run_echo_test(iterations=10000, msg_size=14)




    # msg = b'\xdc\xf5\x06P\xce\x9eZ\xd9\xcf\x10\xa5\xa4\r' # os.urandom(100)
    # b = Bufferizer(msg)
    # d = DeBufferizer()
    # for part in b:
    #     d.add_part(part)
    #     # print(part)
    #     # print(d.get_losts())
    # assert msg == d.get_data()
    # # print(d.get_data())
    # # print(msg)
    # print(d.is_done())
    # # print(d.data_id)
    # # print(len(msg))
    # # print(len(d.get_data()))