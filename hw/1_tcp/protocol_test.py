import os
import random
from contextlib import closing
import platform

import pytest
from testable_thread import TestableThread

from protocol import MyTCPProtocol
from servers import EchoClient, EchoServer, ParallelClientServer

used_ports = {}


def generate_port():
    while True:
        port = random.randrange(25000, 30000)
        if port not in used_ports:
            break
    used_ports[port] = True
    return port


def run_test(client_class, server_class, iterations, msg_size=None):
    a_addr = ('127.0.0.1', generate_port())
    b_addr = ('127.0.0.1', generate_port())

    with closing(MyTCPProtocol(local_addr=a_addr, remote_addr=b_addr)) as a, \
         closing(MyTCPProtocol(local_addr=b_addr, remote_addr=a_addr)) as b:

        client = client_class(a, iterations=iterations, msg_size=msg_size)
        server = server_class(b, iterations=iterations, msg_size=msg_size)

        client_thread = TestableThread(target=client.run)
        server_thread = TestableThread(target=server.run)
        client_thread.daemon = True
        server_thread.daemon = True

        client_thread.start()
        server_thread.start()

        client_thread.join()
        server_thread.join()


current_netem_state = None

def setup_netem(packet_loss, duplicate, reorder):
    global current_netem_state
    if current_netem_state == (packet_loss, duplicate, reorder):
        return
    current_netem_state = (packet_loss, duplicate, reorder)
    netem_cmd = f"tc qdisc replace dev lo root netem loss {packet_loss * 100}% duplicate {duplicate * 100}%"
    if reorder > 0:
        netem_cmd += f" reorder {100 - reorder}%"
    netem_cmd += " delay 10ms rate 1Mbit"
    return_code = os.system(netem_cmd)
    if return_code != 0:
        message = "Could not configure netem. Please check tc executable is available."
        if platform.system() != "Linux":
            message = (
                "Linux is needed in order to execute tests. " +
                "If docker is available, you can use it."
            )
        # Also exits even if not under pytest.
        pytest.exit(message)

@pytest.mark.parametrize("iterations", [10, 50, 100])
@pytest.mark.timeout(30)
def test_basic(iterations):
    setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=11)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_small_loss(iterations):
    setup_netem(packet_loss=0.02, duplicate=0.0, reorder=0.0)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=14)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_small_duplicate(iterations):
    setup_netem(packet_loss=0.0, duplicate=0.02, reorder=0.0)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=14)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_high_loss(iterations):
    setup_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=17)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_high_duplicate(iterations):
    setup_netem(packet_loss=0.0, duplicate=0.1, reorder=0.0)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=14)


@pytest.mark.parametrize("msg_size", [100, 100_000, 5_000_000])
@pytest.mark.timeout(180)
def test_large_message(msg_size):
    setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    run_test(EchoClient, EchoServer, iterations=2, msg_size=msg_size)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(20)
def test_parallel(iterations):
    setup_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    run_test(ParallelClientServer, ParallelClientServer, iterations=iterations)

@pytest.mark.parametrize("iterations", [50_000])
@pytest.mark.timeout(60)
def test_perfomance(iterations):
    setup_netem(packet_loss=0.02, duplicate=0.02, reorder=0.01)
    run_test(EchoClient, EchoServer, iterations=iterations, msg_size=10)
