import os

from protocol import MyTCPProtocol


class Base:
    def __init__(self, socket: MyTCPProtocol, iterations: int, msg_size: int):
        self.socket = socket
        self.iterations = iterations
        self.msg_size = msg_size
        self.success = True

class EchoServer(Base):

    def run(self):
        for _ in range(self.iterations):
            self.socket.send(self.socket.recv(self.msg_size))


class EchoClient(Base):
    
    def run(self):
        for _ in range(self.iterations):
            msg = os.urandom(self.msg_size)
            n = self.socket.send(msg)
            if n != self.msg_size:
                self.success = False
                return
            if msg != self.socket.recv(n):
                self.success = False
                return
            return
