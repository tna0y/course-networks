import os
import argparse
from vpn import VPNManager, TUNInterface, UDPTunnel


def parse_args():
    parser = argparse.ArgumentParser(description='Simple VPN tunnel')
    parser.add_argument('--interface-name', default='tun0',
                      help='Name of the TUN interface (default: tun0)')
    parser.add_argument('--local', default='127.0.0.1:12345',
                      help='Local address and port (default: 127.0.0.1:12345)')
    parser.add_argument('--remote', default='127.0.0.1:54321',
                      help='Remote address and port (default: 127.0.0.1:54321)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    return parser.parse_args()


def main():
    if os.geteuid() != 0:
        print("This program must be run as root!")
        return

    args = parse_args()
    
    local_addr, local_port = args.local.split(':')
    remote_addr, remote_port = args.remote.split(':')

    tun = TUNInterface(args.interface_name)
    udp = UDPTunnel(local_addr, int(local_port), remote_addr, int(remote_port))
    vpn = VPNManager(tun, udp, debug=args.debug)
    
    try:
        vpn.start()
        print("VPN tunnel started. Press Ctrl+C to stop.")
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping VPN tunnel...")
        vpn.stop()

if __name__ == "__main__":
    main()
