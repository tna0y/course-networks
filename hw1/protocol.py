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


class BufferSettings:
    window_size = 2**5
    magic_sep = b'SEP'


class Bufferizer(BufferSettings):
    def __init__(self, data: bytes) -> None:
        super().__init__()
        self.data = data
        if len(data) % self.window_size != 0:
            self.total_parts = len(data) // self.window_size + 1
        else:
            self.total_parts = len(data) // self.window_size

    def __getitem__(self, i):
        part = bytearray()
        part.extend(bytes(str(i), encoding="UTF-8"))
        part.extend(self.magic_sep)
        part.extend(bytes(str(self.total_parts), encoding="UTF-8"))
        part.extend(self.magic_sep)
        part.extend(os.urandom(48))
        part.extend(self.magic_sep)
        part.extend(self.data[i*self.window_size:(i+1)*self.window_size])
        return part

    def __iter__(self):
        for i in range(self.total_parts):
            yield self[i]



class DeBufferizer(BufferSettings):
    def __init__(self) -> None:
        super().__init__()
        self.data_arr = {}
        self.total_parts = None

    def add_part(self, unknown_part):
        sequence_number, _, tail = unknown_part.partition(self.magic_sep)
        total_parts, _, tail = tail.partition(self.magic_sep)
        data_id, _, part_data = tail.partition(self.magic_sep)

        self.data_arr[int(sequence_number)] = part_data
        if self.total_parts is None:
            self.total_parts = int(total_parts)
        else:
            assert self.total_parts == int(total_parts)
        return int(sequence_number)

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    def get_one_lost(self):
        if self.total_parts is None:
            return 'init'
        losts = list(set(range(self.total_parts)) - set(self.data_arr.keys()))
        if len(losts) > 0:
            return losts[0]
        elif len(losts) == 0:
            return 'done'

    def get_data(self):
        data = bytearray()
        for i in range(self.total_parts):
            data.extend(self.data_arr[i])
        return bytes(data)


def get_id(unknown_part):
    sequence_number, _, tail = unknown_part.partition(b'SEP')
    total_parts, _, tail = tail.partition(b'SEP')
    data_id, _, part_data = tail.partition(b'SEP')
    return data_id


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = 2 ** 32
        self.udp_socket.settimeout(0.01)
        self.seen_ids = []

    def send(self, data: bytes):
        b = Bufferizer(data)
        for part in b:
            self.sendto(part)
        while True:
            try:
                resp = self.recvfrom(self.max_size)
                print('send resp', resp)
                if resp == b'END':
                    # print('send end')
                    return len(data)
                if resp == b'PENDING':
                    self.sendto(b[0])
                    # print('send pending here')
                if resp.startswith(b'GET'):
                    lost_part = int(resp.removeprefix(b'GET'))
                    self.sendto(b[lost_part])
                    print(f'send {lost_part} {b[lost_part]}')
            except TimeoutError:
                # print('send pending')
                self.sendto(b'PENDING')

        return len(data)

    def recv(self, n: int):
        d = DeBufferizer()
        while not d.is_done():
            try:
                data_part = self.recvfrom(self.max_size)
                id = get_id(data_part)
                if id in self.seen_ids:
                    continue
                print('recv resp', data_part)
                self.seen_ids.append(id)
                if data_part == b'END':
                    # print('recv end')
                    pass
                elif data_part == b'PENDING':
                    # print('recv pending')
                    lost_status = d.get_one_lost()
                    if lost_status == 'init':
                        self.sendto(b'GET' + bytes(str(0), encoding="UTF-8"))
                    elif lost_status == 'done':
                        for _ in range(20):
                            self.sendto(b'END')
                    else:
                        self.sendto(b'GET' + bytes(str(lost_status), encoding="UTF-8"))
                else:
                    add_number = d.add_part(data_part)
                    lost_status = d.get_one_lost()
                    print(f'add data {add_number} lost_status: {lost_status}')
                    if lost_status == 'init':
                        self.sendto(b'GET' + bytes(str(0), encoding="UTF-8"))
                    elif lost_status == 'done':
                        for _ in range(20):
                            self.sendto(b'END')
                    else:
                        print(f'recv get {str(lost_status)}')
                        self.sendto(b'GET' + bytes(str(lost_status), encoding="UTF-8"))
            except TimeoutError:
                print('recv pending')
                self.sendto(b'PENDING')
        
        return d.get_data()
        
        


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    run_echo_test(iterations=2, msg_size=100_000)



    # msg = os.urandom(10000)
    # b = Bufferizer(msg)
    # print(b.total_parts)
    # d = DeBufferizer()
    # print(d.get_one_lost())
    # print(b[0])
    # d.add_part(b[0])
    # lost = d.get_one_lost()
    # print(lost, b[lost])
    # d.add_part(b[lost])
    # lost = d.get_one_lost()
    # print(lost, b[lost])


# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms