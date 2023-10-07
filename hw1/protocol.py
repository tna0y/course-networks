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
    window_size = 2**15
    magic_sep = b'SEP'


class Bufferizer(BufferSettings):
    def __init__(self, data: bytes) -> None:
        super().__init__()
        self.data = data
        self.id = os.urandom(24)
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
        part.extend(self.id)
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
        self.id = None

    def add_part(self, unknown_part):
        sequence_number, _, tail = unknown_part.partition(self.magic_sep)
        total_parts, _, tail = tail.partition(self.magic_sep)
        data_id, _, part_data = tail.partition(self.magic_sep)

        self.data_arr[int(sequence_number)] = part_data
        if self.id is None:
            self.id = data_id
        elif self.id == data_id:
            pass
        else:
            raise ValueError(data_id)
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
        self.udp_socket.settimeout(0.1)
        self.broken_ids = []

    def send(self, data: bytes):
        b = Bufferizer(data)

        if b.total_parts == 1:
            for part in b:
                self.sendto(part)


        while True:
            try:
                resp = self.recvfrom(self.max_size)
                # print('send resp', resp)
                if resp.startswith(b'END'):
                    if b.id == resp.removeprefix(b'END'):
                        return len(data)
                # elif resp.startswith(b'PENDING'):

                
                elif resp.startswith(b'GET'):
                    lost_part = int(resp.removeprefix(b'GET'))
                    self.sendto(b[lost_part])
                    # print(f'send {lost_part} {b[lost_part]}')
                else:
                    print('else', resp)
                    return len(data)
                    # self.broken_ids.append(get_id(resp))
                    # print('======else', resp)
                    # id = get_id(resp)
                    # print(id.hex(), b.id.hex())
                    # if id == b.id:
                    #     print('==========================================RET')
                    #     return len(data)
            except TimeoutError:
                self.sendto(b[0])

        return len(data)

    def recv(self, n: int):
        def abort(id):
            for _ in range(1):
                self.sendto(b'END' + id)

        d = DeBufferizer()

        try:
            data_part = self.recvfrom(self.max_size)
            print('recv 1data', data_part)
            if not data_part.startswith(b'END') and not data_part.startswith(b'PENDING') and not data_part.startswith(b'GET'):
                d.add_part(data_part)
                if d.is_done():
                    abort(d.id)
                    return d.get_data()
        except TimeoutError:
            d = DeBufferizer()

        while not d.is_done():
            try:
                data_part = self.recvfrom(self.max_size)
                print('recv data', data_part)
                if data_part.startswith(b'END'):
                    pass
                elif data_part.startswith(b'GET'):
                    pass
                else:
                    try:
                        add_number = d.add_part(data_part)
                    except ValueError as err:
                        with open('error.txt', 'w+') as f:
                            f.write(repr(err))
                        continue
                    lost_status = d.get_one_lost()
                    # print(f'add data {add_number} lost_status: {lost_status}')
                    if lost_status == 'init':
                        self.sendto(b'GET' + bytes(str(0), encoding="UTF-8"))
                    elif lost_status == 'done':
                        abort(d.id)
                        return d.get_data()
                    else:
                        # print(f'recv get {str(lost_status)}')
                        self.sendto(b'GET' + bytes(str(lost_status), encoding="UTF-8"))
            except TimeoutError:
                print('TO')
                self.sendto(b'GET' + bytes(str(0), encoding="UTF-8"))
                # print('recv pending')
                # self.sendto(b'PENDING' + d.id)

        # for _ in range(20):
        #     self.sendto(b'END')
        return d.get_data()
        
        


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    # setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=2, msg_size=100_000)


    setup_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
    run_echo_test(iterations=100, msg_size=17)



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