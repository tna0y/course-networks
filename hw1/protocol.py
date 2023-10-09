import socket
import os
import time
from collections import OrderedDict
import functools


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
        self.id = os.urandom(10)
        if len(data) % WINDOW_SIZE != 0:
            self.total_parts = len(data) // WINDOW_SIZE + 1
        else:
            self.total_parts = len(data) // WINDOW_SIZE

    def __getitem__(self, i):
        part = bytearray()
        part.extend(b'DATA')
        part.extend(SEP)
        part.extend(self.id)
        part.extend(SEP)
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
        _, id, part_n, total_parts, data = unknown_part.split(SEP, maxsplit=4)

        if self.id is None:
            self.id = id
        else:
            assert self.id == id
        if self.total_parts is None:
            self.total_parts = int(total_parts)
            self.parts_set = set(range(self.total_parts))
        else:
            assert self.total_parts == int(total_parts)

        self.data_arr[int(part_n)] = data

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    def get_losts_request(self):
        losts = list(self.parts_set - set(self.data_arr.keys()))
        if len(losts) == 0:
            return b'OK' + self.id
        else:
            return b'GET' + SEP + self.id + SEP + bytes(str(losts[0]), encoding="UTF-8") 

    def get_data(self):
        data = bytearray()
        for i in range(self.total_parts):
            data.extend(self.data_arr[i])
        return bytes(data)


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = 2 ** 32
        self.udp_socket.settimeout(0.1)
        self.send_buffer = OrderedDict()
        self.recv_buffer = []

    def send(self, send_data: bytes):
        b = Bufferizer(send_data)
        self.send_buffer[b.id] = b
        for part in b:
            self.sendto( part)

        while len(self.send_buffer):
            try:
                data = self.recvfrom(self.max_size)
                
                if data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    if okid in self.send_buffer.keys():
                        del_item = self.send_buffer.pop(okid)
                elif data.startswith(b'GET'):
                    _, id, lost_part = data.split(SEP)
                    try:
                        if id == b'NEW':
                            for part in b:
                                self.sendto( part)
                            self.sendto( b'APPROVE' + b.id)
                        else:
                            self.sendto( self.send_buffer[id][int(lost_part)])
                    except KeyError:
                        pass
                elif data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto( b'OK' + id)
                elif data.startswith(b'DATA'):
                    self.sendto( b'APPROVE' + list(self.send_buffer.keys())[0])
            except TimeoutError:
                for part in b:
                    self.sendto( part)
                self.sendto( b'APPROVE' + b.id)

        return len(send_data)

    def recv(self, n: int):
        d = DeBufferizer()
        while not d.is_done():
            try:
                data = self.recvfrom(self.max_size)
                if data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto( b'OK' + id)
                    elif id == d.id:
                        self.sendto(  d.get_losts_request())
                    else:
                        self.sendto( b'GET' + SEP + b'NEW' + SEP + b'_')
                elif data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    self.recv_buffer.append(okid)
                elif data.startswith(b'DATA'):
                    _, id, _ = data.split(SEP, 2)
                    if d.id is None or d.id == id:
                        d.add_part(data)
                        self.sendto( d.get_losts_request())

            except TimeoutError:
                pass

        self.recv_buffer.append(d.id)
        return d.get_data()
        
        


if __name__ == "__main__":
    from protocol_test import *
    
    def log_time(timeout):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                print(func.__name__, end='... ')
                t = time.time()
                func(*args, **kwargs)
                print(f'{round(time.time() - t, 2)}/{timeout} seconds.')
            return wrapper
        return decorator

    @log_time(20)
    def test_basic():
        for iterations in [10, 100, 1000]:
            setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
            run_echo_test(iterations=iterations, msg_size=11)
    @log_time(20)
    def test_small_loss():
        for iterations in [10, 100, 1000]:
            setup_netem(packet_loss=0.02, duplicate=0.0, reorder=0.0)
            run_echo_test(iterations=iterations, msg_size=14)
    @log_time(20)
    def test_small_duplicate():
        for iterations in [10, 100, 1000, 5000]:
            setup_netem(packet_loss=0.0, duplicate=0.02, reorder=0.0)
            run_echo_test(iterations=iterations, msg_size=14)
    @log_time(20)
    def test_high_loss():
        for iterations in [10, 100, 1000]:
            setup_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
            run_echo_test(iterations=iterations, msg_size=17)
    @log_time(20)
    def test_high_duplicate():
        for iterations in [10, 100, 1000]:
            setup_netem(packet_loss=0.0, duplicate=0.1, reorder=0.0)
            run_echo_test(iterations=iterations, msg_size=14)
    @log_time(180)
    def test_large_message():
        for msg_size in [100, 100_000, 10_000_000]:
            setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
            run_echo_test(iterations=2, msg_size=msg_size)
    @log_time(60)
    def test_perfomance():
        for iterations in [50_000]:
            setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
            run_echo_test(iterations=iterations, msg_size=10)

    test_basic()
    test_small_loss()
    test_small_duplicate()
    test_high_loss()
    test_high_duplicate()
    test_large_message()
    test_perfomance()


# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms