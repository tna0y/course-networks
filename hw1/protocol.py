import socket
import os
import time
from collections import OrderedDict
import functools

import logging

logging.basicConfig(format='%(message)s',
                    level=logging.INFO,
                    handlers=[logging.FileHandler("main_double.logs"),
                              logging.StreamHandler()])


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


WINDOW_SIZE = 2 ** 15
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
        part.extend(self.data[i * WINDOW_SIZE:(i + 1) * WINDOW_SIZE])
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

    def sendto(self, send_data: bytes, who_am_i: str = 'unknown'):
        logging.info(who_am_i + ' SEND ' + str(bytes(send_data)))
        super().sendto(send_data)

    def recvfrom(self, send_data: bytes, who_am_i: str = 'unknown'):
        data = super().recvfrom(send_data)
        logging.info(who_am_i + ' GETS ' + str(bytes(data)))
        return data

    def send(self, send_data: bytes, who_am_i: str = 'unknown'):
        who_am_i += 'send '
        b = Bufferizer(send_data)
        self.send_buffer[b.id] = b
        for part in b:
            self.sendto(part, who_am_i)
        #     self.sendto(part, who_am_i)

        # data = self.recvfrom(self.max_size, who_am_i)
        # if data.startswith(b'OK'):
        #     okid = data.removeprefix(b'OK')
        #     if okid in self.send_buffer.keys():
        #         del_item = self.send_buffer.pop(okid)

        while len(self.send_buffer):
            try:
                data = self.recvfrom(self.max_size, who_am_i)

                if data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    if okid in self.send_buffer.keys():
                        del_item = self.send_buffer.pop(okid)
                        logging.info(who_am_i + 'DEL ID' + str(del_item.id))
                    else:
                        logging.info(who_am_i + 'Duplicate ok')
                elif data.startswith(b'GET'):
                    try:
                        _, id, lost_part = data.split(SEP)
                        if id == b'NEW':
                            for part in b:
                                self.sendto(part, who_am_i)
                            self.sendto(b'APPROVE' + b.id, who_am_i)
                        else:
                            self.sendto(self.send_buffer[id][int(lost_part)], who_am_i)
                    except KeyError:
                        logging.info(who_am_i + 'Key')
                elif data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto(b'OK' + id, who_am_i)
                    else:
                        logging.info(who_am_i + 'not in buffer' + str(id))
                elif data.startswith(b'DATA'):
                    self.sendto(b'APPROVE' + list(self.send_buffer.keys())[0], who_am_i)
                else:
                    logging.info(who_am_i + 'WTF2' + str(data))
            except TimeoutError:
                logging.info(who_am_i + 'ToE')
                for part in b:
                    self.sendto(part, who_am_i)
                self.sendto(b'APPROVE' + b.id, who_am_i)

        logging.info(who_am_i + 'Closed')
        return len(send_data)

    def recv(self, n: int, who_am_i: str = 'unknown'):
        who_am_i += 'recv '
        d = DeBufferizer()
        while not d.is_done():
            try:
                data = self.recvfrom(self.max_size, who_am_i)
                if data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto(b'OK' + id, who_am_i)
                    elif id == d.id:
                        self.sendto(d.get_losts_request(), who_am_i)
                    else:
                        self.sendto(b'GET' + SEP + b'NEW' + SEP + b'_', who_am_i)
                elif data.startswith(b'GET'):
                    logging.info(who_am_i + 'pass recv get')
                elif data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    self.recv_buffer.append(okid)
                elif data.startswith(b'DATA'):
                    _, id, _ = data.split(SEP, 2)
                    if d.id is None or d.id == id:
                        d.add_part(data)
                        self.sendto(d.get_losts_request(), who_am_i)
                    else:
                        logging.info(who_am_i + 'duplicate')
                else:
                    logging.info(who_am_i + 'WTF' + str(data))

            except TimeoutError:
                logging.info(who_am_i + 'ToE')

        self.recv_buffer.append(d.id)
        logging.info(who_am_i + 'Closed')
        return d.get_data()


if __name__ == "__main__":
    from protocol_test import *

    t = time.time()
    for iterations in [1000]:
        setup_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
        run_echo_test(iterations=iterations, msg_size=17)
    logging.info('=============')
    logging.info(time.time() - t)

# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms
