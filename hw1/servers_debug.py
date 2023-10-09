import os
import time

from protocol import MyTCPProtocol


class Base:
    def __init__(self, socket: MyTCPProtocol, iterations: int, msg_size: int):
        self.socket = socket
        self.iterations = iterations
        self.msg_size = msg_size


class EchoServer(Base):

    def run(self):
        for i in range(self.iterations):
            msg = self.socket.recv(self.msg_size, f'SERVER {i} ')
            print(f'===== {i}')
            self.socket.send(msg, f'SERVER {i} ')
            
class EchoClient(Base):

    def run(self):
        for i in range(self.iterations):
            msg = os.urandom(self.msg_size)
            print(f'========================================================== MSG {i}', msg)
            n = self.socket.send(msg, f'CLIENT {i} ')
            
            recv_msg = self.socket.recv(n, f'CLIENT {i} ')
            assert n == self.msg_size
            assert msg == recv_msg
            print(f'========================================================= DONE {i}')
