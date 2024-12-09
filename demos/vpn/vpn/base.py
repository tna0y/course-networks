from abc import ABC, abstractmethod

class TunnelInterface(ABC):
    @abstractmethod
    def read(self) -> bytes:
        pass
    
    @abstractmethod
    def write(self, data: bytes) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass 