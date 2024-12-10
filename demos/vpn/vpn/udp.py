import socket
from .base import TunnelInterface

class UDPTransport(TunnelInterface):
    def __init__(self, local_addr: str, local_port: int, remote_addr: str, remote_port: int):
        self.socket = None 
        self.remote_addr = (remote_addr, remote_port)

    def read(self) -> bytes:
        """
        Чтение данных из UDP-сокета
        """
        pass

    def write(self, data: bytes) -> None:
        """
        Отправка данных через UDP-сокет
        """
        pass

    def close(self) -> None:
        """
        Закрытие сокета
        """
        pass