import fcntl
import struct
from .base import TunnelInterface

    
class TUNInterface(TunnelInterface):
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000
    
    def __init__(self, name="tun0"):
        self.name = name
        self._setup_interface()
    
    def _setup_interface(self):
        self.tun = open('/dev/net/tun', 'r+b', buffering=0)
        ifr = struct.pack('16sH', self.name.encode(), self.IFF_TUN | self.IFF_NO_PI)
        fcntl.ioctl(self.tun, self.TUNSETIFF, ifr)
    
    def read(self) -> bytes:
        return self.tun.read(2048)
    
    def write(self, data: bytes) -> None:
        self.tun.write(data)
    
    def close(self) -> None:
        self.tun.close() 