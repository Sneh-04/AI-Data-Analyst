from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENTS_DIR))


def pytest_configure(config):
    config.addinivalue_line("markers", "network: requires access to OpenML.")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_OPENML_TESTS") == "1":
        return
    skip_network = pytest.mark.skip(reason="Set RUN_OPENML_TESTS=1 to run OpenML network tests.")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_network)
