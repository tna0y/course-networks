import pytest
import pkgutil

def pytest_configure(config):
    found_pytest_timeout = False
    for pkg in pkgutil.iter_modules():
        if pkg.name == "pytest_timeout":
             found_pytest_timeout = True
             break
    if not found_pytest_timeout:
        pytest.exit(
            "pytest-timeout not found. Please install it via package manager " +
            "(usually, package name is python3-pytest-timeout) or pip " +
            "(sudo pip install python3-pytest-timeout)."
        )
