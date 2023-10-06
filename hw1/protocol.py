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
    window_size = 2**12
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
        part.extend(bytes(str(i+1), encoding="UTF-8"))
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

    def add_part(self, unknown_part, seen_ids):
        sequence_number, _, tail = unknown_part.partition(self.magic_sep)
        total_parts, _, tail = tail.partition(self.magic_sep)
        data_id, _, part_data = tail.partition(self.magic_sep)

        # print(f"REC PART ===", data_id.hex(), int(sequence_number),"/", int(total_parts), part_data.hex())
        if data_id not in seen_ids:
            seen_ids.append(data_id)
            self.data_arr[int(sequence_number)] = part_data
            if self.total_parts is None:
                self.total_parts = int(total_parts)
            else:
                assert self.total_parts == int(total_parts)
            print('TP', self.total_parts)

    def is_done(self) -> bool:
        return len(self.data_arr) == self.total_parts

    def losts(self):
        if self.total_parts is None:
            return None
        return list(set(range(1, self.total_parts+1)) - set(self.data_arr.keys()))

    def get_data(self):
        data = bytearray()
        for i in range(1, self.total_parts+1):
            data.extend(self.data_arr[i])
        return bytes(data)


class MyTCPProtocol(UDPBasedProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_ids = []
        self.max_size = 2 ** 32

    def send(self, data: bytes):
        b = Bufferizer(data)
        for data_part in b:
            self.sendto(data_part)

        # recv_done = False
        # while not recv_done:
        #     data = self.recvfrom(self.max_size)
        #     if data.startswith(b'ASK'):
        #         print('SENER NOTIFICATED')
        #     elif data.startswith(b'DONE'):
        #         recv_done = True
        return len(data)

    def recv(self, n: int):
        d = DeBufferizer()
        data_part = self.recvfrom(self.max_size)
        if not data_part.startswith(b'ASK') and not data_part.startswith(b'DONE'):
            d.add_part(data_part, self.seen_ids)
            while len(d.losts()) > 0:
                ask_part = bytearray()
                ask_part.extend(b'ASK')
                ask_part.extend(bytes(str(d.losts()[0]), encoding="UTF-8"))
                self.sendto(ask_part)

            return d.get_data()
        elif data_part.startswith(b'ASK'):
            return data_part
        elif data_part.startswith(b'DONE'):
            return data_part
        
        # while not d.is_done():
        #     if len(d.get_one_lost()) > 0:
        #         lost_part = d.get_one_lost()
        #         ask_for_lost = bytearray()
        #         ask_for_lost.extend(b'ASK')
        #         ask_for_lost.extend(lost_part[0])
        #         self.sendto(ask_for_lost)
        #     else:
        #         print('WTF???')
        
        


if __name__ == "__main__":
    from protocol_test import setup_netem, run_echo_test
    # msg_size = 10_000_000
    # setup_netem(packet_loss=0.00, duplicate=0.00, reorder=0.00)
    # run_echo_test(iterations=2, msg_size=msg_size)

    # setup_netem(packet_loss=0.00, duplicate=0.00, reorder=0.00)
    # run_echo_test(iterations=2, msg_size=16)

    # setup_netem(packet_loss=0.0, duplicate=0.02, reorder=0.0)
    # run_echo_test(iterations=5000, msg_size=14)

    setup_netem(packet_loss=0.7, duplicate=0.02, reorder=0.01)
    run_echo_test(iterations=2, msg_size=10)

    # seen_ids = []
    # msg = b'\xdc\xf5\x06P\xce\x9eZ\xd9\xcf\x10\xa5\xa4\r'
    # msg = os.urandom(10_000_000)

    # b = Bufferizer(msg)
    # d = DeBufferizer()
    # for part in b:
    #     d.add_part(part, seen_ids)
    # assert msg == d.get_data()
    # print(d.is_done())


# Сброс кривых параметров (из-за которых в том числе может отваливаться VSCode remote)
# tc qdisc replace dev lo root netem loss 0% duplicate 0% reorder 0% delay 0ms