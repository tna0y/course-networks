import socket
import json
import base64
import os
import random
import time


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


WINDOW_SIZE = 2**15
SEP = b'SEP'


class Bufferizer:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.id = os.urandom(32)
        if len(data) % WINDOW_SIZE != 0:
            self.total_parts = len(data) // WINDOW_SIZE + 1
        else:
            self.total_parts = len(data) // WINDOW_SIZE

    def __getitem__(self, i):
        part = bytearray()
        part.extend(b'DATA')
        part.extend(SEP)
        part.extend(self.id)
        part.extend(bytes(str(i), encoding="UTF-8"))
        part.extend(SEP)
        part.extend(bytes(str(self.total_parts), encoding="UTF-8"))
        part.extend(SEP)
        part.extend(self.data[i*WINDOW_SIZE:(i+1)*WINDOW_SIZE])
        return part

    def __iter__(self):
        for i in range(self.total_parts):
            yield self[i]



class DeBufferizer:
    def __init__(self) -> None:
        self.data_arr = {}
        self.total_parts = None
        self.id = None

    def add_part(self, unknown_part):
        _, id, part_n, total_parts, data = unknown_part.split(SEP)

        if self.id is None:
            self.id = id
        else:
            assert self.id == id
        if self.total_parts is None:
            self.total_parts = int(total_parts)
        else:
            assert self.total_parts == int(total_parts)

        self.data_arr[int(part_n)] = data
        return

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    def get_losts_request(self):
        if self.total_parts is None:
            raise ValueError('Get losts of not initialized DeBufferizer')
        losts = list(set(range(self.total_parts)) - set(self.data_arr.keys()))
        if len(losts) > 0:
            return f'{sss}'.join(losts)
        else:
            seen_ids.add(self.id)
            return 'done'
        
    def get_lost_len(self):
        if self.total_parts is None:
            return 'init'
        losts = list(set(range(self.total_parts)) - set(self.data_arr.keys()))
        return len(losts)

    def get_data(self):
        data = bytearray()
        for i in range(self.total_parts):
            data.extend(self.data_arr[i])
        return bytes(data)


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = 2 ** 32
        self.udp_socket.settimeout(0.001)
        self.send_buffer = {}
        self.recv_buffer = {}

    def send(self, data: bytes):

        while len(self.send_buffer):
            try:
                id = self.send_buffer.keys()[0]
                self.sendto(b'APPROVE' + id)
                data = self.recvfrom(self.max_size)
                if data == b'OK' + id:
                    self.send_buffer.pop(id)
                elif data.startswith('GET'):
                    print('GET')
            except TimeoutError:
                pass


        b = Bufferizer(data)
        self.send_buffer[b.id] = b
        for part in b:
            self.sendto(part)

        return len(data)

    def recv(self, n: int):
        d = DeBufferizer()
        while not d.is_done(self.seen_ids):
            try:
                data = self.recvfrom(self.max_size)
                if data.startswith(b'APPROVE'):
                    pass
                elif data.startswith(b'GET'):
                    pass
                elif data.startswith(b'DATA'):
                    d.add_part(data_part, self.seen_ids)
            except TimeoutError:
                pass
        
        return d.get_data()
        
        


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    setup_netem(packet_loss=0.0, duplicate=0.02, reorder=0.01)
    run_echo_test(iterations=2, msg_size=10_000_000)

    # import time
    # t = time.time()
    # setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=1000, msg_size=10)
    # print(time.time() - t)

    # setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=2, msg_size=100)
    # setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    # run_echo_test(iterations=1000, msg_size=11)


# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms