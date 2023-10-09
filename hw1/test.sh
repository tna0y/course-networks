#!/usr/bin/env bash
set -xeu pipefail

pytest -v protocol_test.py --durations=0 -o log_cli=true
