from scapy.layers.inet import IP
import threading
from .base import TunnelInterface

class VPNManager:
    def __init__(self, interface: TunnelInterface, transport: TunnelInterface, debug=False):
        self.interface = interface
        self.transport = transport
        self.running = False
        self.debug = debug
        
    def _debug_packet(self, data: bytes, direction: str):
        if not self.debug:
            return
            
        try:
            packet = IP(data)
            print(f"{direction} {packet.src} > {packet.dst}, proto {packet.proto}, length {len(data)}")
        except:
            print(f"{direction} Unknown packet type")
            return
    def start(self):
        self.running = True
        
        self.interface_to_transport = threading.Thread(
            target=self._forward_packets,
            args=(self.interface, self.transport)
        )
        self.transport_to_interface = threading.Thread(
            target=self._forward_packets,
            args=(self.transport, self.interface)
        )
        
        self.interface_to_transport.start()
        self.transport_to_interface.start()
    
    def stop(self):
        self.running = False
        self.interface.close()
        self.transport.close()
        self.interface_to_transport.join()
        self.transport_to_interface.join()
    
    def _forward_packets(self, source: TunnelInterface, destination: TunnelInterface):
        source_name = "Interface" if source == self.interface else "Transport"
        dest_name = "Transport" if source == self.interface else "Interface"
        
        while self.running:
            try:
                data = source.read()
                if data:
                    self._debug_packet(data, f"{source_name} -> {dest_name}")
                    destination.write(data)
            except Exception as e:
                print(f"Error forwarding packets: {e}")
                break