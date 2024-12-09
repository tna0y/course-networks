import socket
from .base import TunnelInterface

class UDPTunnel(TunnelInterface):
    def __init__(self, local_addr: str, local_port: int, remote_addr: str, remote_port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_addr, local_port))
        self.remote_addr = (remote_addr, remote_port)
    
    def read(self) -> bytes:
        data, _ = self.socket.recvfrom(2048)
        return data
    
    def write(self, data: bytes) -> None:
        self.socket.sendto(data, self.remote_addr)
    
    def close(self) -> None:
        self.socket.close() 