import socket
import json
import base64
import os
import random
import time
from collections import OrderedDict
import logging

logging.basicConfig(level=logging.WARNING)


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
        if self.total_parts is None:
            raise ValueError('Get losts of not initialized DeBufferizer')
        # str_ints = list(map(str, ))
        # print(str_ints)
        # losts = list(map(bytes, encoding="UTF-8"), str_ints))
        # print(losts)
        losts = list(self.parts_set - set(self.data_arr.keys()))
        if len(losts) > 0:
            return b'GET' + SEP + self.id + SEP + bytes(str(losts[0]), encoding="UTF-8") 
        else:
            return b'OK' + self.id

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

    def sendto(self, mytype:str, data:bytes):
        logging.info(str(mytype) + ' SEND', bytes(data))
        super().sendto(data)

    def recvfrom(self, mytype, n):
        data = super().recvfrom(n)
        logging.info(str(mytype)+ ' GETS', bytes(data))
        return data

    def send(self, mytype:str, send_data: bytes):
        mytype += ' send'

        b = Bufferizer(send_data)
        self.send_buffer[b.id] = b
        for part in b:
            self.sendto(mytype, part)
        # self.sendto(mytype, b'APPROVE' + b.id)

        to_i = 0
        while len(self.send_buffer):
            try:
                data = self.recvfrom(mytype,self.max_size)
                
                if data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    if okid in self.send_buffer.keys():
                        del_item = self.send_buffer.pop(okid)
                        logging.info(mytype, 'DEL ID', del_item.id)
                    else:
                        logging.info(mytype, 'Duplicate ok')
                elif data.startswith(b'GET'):
                    logging.info('sssss')
                    try:
                        _, id, lost_part = data.split(SEP)
                        if id == b'NEW':
                            for part in b:
                                self.sendto(mytype, part)
                            self.sendto(mytype, b'APPROVE' + b.id)
                        else:
                            self.sendto(mytype, self.send_buffer[id][int(lost_part)])
                    except KeyError:
                        logging.info('Key')
                        pass
                elif data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto(mytype, b'OK' + id)
                        logging.info(mytype, 'break loop')
                    else:
                        logging.info(mytype, 'not in buffer', id)
                elif data.startswith(b'DATA'):
                    # pass
                    # logging.info('app')
                    self.sendto(mytype, b'APPROVE' + list(self.send_buffer.keys())[0])
                else:
                    logging.info(mytype, 'WTF2', data)
            except TimeoutError:
                for part in b:
                    self.sendto(mytype, part)
                self.sendto(mytype, b'APPROVE' + b.id)
                logging.info(mytype, 'ToE')

        logging.info(mytype, 'Closed')
        return len(send_data)

    def recv(self, mytype:str, n: int):
        mytype += ' recv'
        d = DeBufferizer()
        while not d.is_done():
            try:
                data = self.recvfrom(mytype,self.max_size)
                # logging.info(mytype, data)
                if data.startswith(b'APPROVE'):
                    id = data.removeprefix(b'APPROVE')
                    if id in self.recv_buffer:
                        self.sendto(mytype, b'OK' + id)
                    elif id == d.id:
                        self.sendto(mytype,  d.get_losts_request())
                    else:
                        self.sendto(mytype, b'GET' + SEP + b'NEW' + SEP + b'_')
                elif data.startswith(b'GET'):
                    logging.info('here')
                elif data.startswith(b'OK'):
                    okid = data.removeprefix(b'OK')
                    self.recv_buffer.append(okid)
                elif data.startswith(b'DATA'):
                    _, id, _ = data.split(SEP, 2)
                    if d.id is None or d.id == id:
                        d.add_part(data)
                        self.sendto(mytype, d.get_losts_request())
                        # logging.info('add data', d.is_done(), d.id, d.get_losts_request())
                    else:
                        logging.info(mytype, 'duplicate')
                else:
                    logging.info(mytype, 'WTF', data)

            except TimeoutError:
                logging.info(mytype, 'ToE')
                # self.sendto(mytype, b'GET' + SEP + b'NEW' + SEP + b'_')
        
        # logging.info('done')
        self.recv_buffer.append(d.id)
        logging.info(mytype, 'Closed')
        return d.get_data()
        
        


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    # setup_netem(packet_loss=0.0, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=2, msg_size=10_000_000)

    # setup_netem(packet_loss=0.01, duplicate=0.0, reorder=0.0)
    # run_echo_test(iterations=100, msg_size=14)

    # setup_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
    # run_echo_test(iterations=1000, msg_size=14)
    setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    run_echo_test(iterations=2, msg_size=10_000_000)

    # import time
    # t = time.time()
    # setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=1000, msg_size=10)
    # logging.info(time.time() - t)

    # setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    # run_echo_test(iterations=2, msg_size=100)
    # setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    # run_echo_test(iterations=1000, msg_size=11)


# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms