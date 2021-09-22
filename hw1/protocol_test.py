import random

import pytest
from testable_thread import TestableThread

from protocol import MyTCPProtocol
from servers import EchoClient, EchoServer

used_ports = {}


def generate_port():
    while True:
        port = random.randrange(25000, 30000)
        if port not in used_ports:
            break
    used_ports[port] = True
    return port


def run_echo_test(iterations, packet_loss, msg_size):
    a_addr = ('127.0.0.1', generate_port())
    b_addr = ('127.0.0.1', generate_port())

    a = MyTCPProtocol(local_addr=a_addr, remote_addr=b_addr, send_loss=packet_loss)
    b = MyTCPProtocol(local_addr=b_addr, remote_addr=a_addr, send_loss=packet_loss)

    client = EchoClient(a, iterations=iterations, msg_size=msg_size)
    server = EchoServer(b, iterations=iterations, msg_size=msg_size)

    client_thread = TestableThread(target=client.run)
    server_thread = TestableThread(target=server.run)
    client_thread.daemon = True
    server_thread.daemon = True

    client_thread.start()
    server_thread.start()

    client_thread.join()
    server_thread.join()


@pytest.mark.parametrize("iterations", [10, 100, 1000, 10000])
@pytest.mark.timeout(5)
def test_basic(iterations):
    run_echo_test(iterations=iterations, packet_loss=0.0, msg_size=11)


@pytest.mark.parametrize("iterations", [10, 100, 1000, 5000])
@pytest.mark.timeout(10)
def test_small_loss(iterations):
    run_echo_test(iterations=iterations, packet_loss=0.02, msg_size=14)


@pytest.mark.parametrize("iterations", [10, 100, 1000, 5000])
@pytest.mark.timeout(10)
def test_high_loss(iterations):
    run_echo_test(iterations=iterations, packet_loss=0.1, msg_size=17)


@pytest.mark.parametrize("msg_size", [100, 100_000, 10_000_000])
@pytest.mark.timeout(30)
def test_large_message(msg_size):
    run_echo_test(iterations=2, packet_loss=0.02, msg_size=msg_size)


@pytest.mark.parametrize("iterations", [50_000])
@pytest.mark.timeout(30)
def test_perfomance(iterations):
    run_echo_test(iterations=iterations, packet_loss=0.02, msg_size=10)


