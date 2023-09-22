#!/usr/bin/env bash
set -xeuo pipefail
ip netns del virtual_net0 || true
ip netns add virtual_net0 || true
ip netns exec virtual_net0 ip link set dev lo up
ip netns exec virtual_net0 pytest -v protocol_test.py -o log_cli=true