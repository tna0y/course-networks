#!/usr/bin/env bash
set -xeuo pipefail

pytest -v protocol_test.py -o log_cli=true --durations=0
