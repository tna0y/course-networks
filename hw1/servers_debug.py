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
            msg = self.socket.recv(f'SERVER {i}', self.msg_size)
            # print('=========================server', i, 'MSG:', msg)
            print(f'===== {i}')
            # time.sleep(0.5)
            self.socket.send(f'SERVER {i}',msg)
            
class EchoClient(Base):

    def run(self):
        for i in range(self.iterations):
            msg = os.urandom(self.msg_size)
            print(f'=========================================================== MSG {i}', msg)
            n = self.socket.send(f'CLIENT {i}', msg)
            
            recv_msg = self.socket.recv(f'CLIENT {i}', n)
            # if msg != recv_msg:
            #     print(msg, recv_msg)
            assert n == self.msg_size
            assert msg == recv_msg
            print(f'========================================================= DONE {i}')
            # time.sleep(0.5)
            # print('=========================DONE', i, 'MSG:', msg)
        # print("===i===", self.socket.i)
