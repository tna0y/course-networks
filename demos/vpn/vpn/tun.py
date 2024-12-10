import fcntl
import os
import struct
from .base import TunnelInterface

class TUNInterface(TunnelInterface):
    TUNSETIFF = 0x400454ca
    IFF_TUN   = 0x0001
    IFF_NO_PI = 0x1000

    def __init__(self, name="tun0"):
        self.name = name
        self._setup_interface()

    def _setup_interface(self):
        """
        Настройка интерфейса
        """
        pass

    def read(self) -> bytes:
        """
        Чтение данных из интерфейса
        """
        pass

    def write(self, data: bytes) -> None:
        """
        Запись данных в интерфейс
        """
        pass

    def close(self) -> None:
        """
        Закрытие интерфейса
        """
        pass