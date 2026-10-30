"""Tier configuration for the test suite.

Every test file lives in one of the tier folders under tests/. The tier marker
comes from the folder, so no test declares it by hand: `pytest -m unit` selects
tests/unit/, and the other tiers work the same way. Unit tests are deterministic
and need no external services, network access, or sibling repos.
"""

import os
from pathlib import Path

import pytest

TESTS_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Tier folder under tests/ -> marker name. The placement checker reads this dictionary by AST.
DIRECTORY_MARKERS = {"unit": "unit", "integration": "integration", "contract": "contract", "host": "host", "e2e": "e2e"}

TIER_DESCRIPTIONS = {
    "unit": "deterministic, isolated, no external dependencies",
    "integration": "uses the network, a subprocess, a live service, or live repo state",
    "contract": "checks an interface contract between components",
    "host": "runs on the real host (services, sibling repos, LXC); never in CI",
    "e2e": "end-to-end tests of a whole workflow",
}


def pytest_configure(config: pytest.Config) -> None:
    for folder, marker in DIRECTORY_MARKERS.items():
        config.addinivalue_line("markers", f"{marker}: {TIER_DESCRIPTIONS[folder]}")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark every collected test with the tier of the folder it lives in."""
    for item in items:
        for folder, marker in DIRECTORY_MARKERS.items():
            if Path(item.path).is_relative_to(TESTS_DIR / folder):
                item.add_marker(getattr(pytest.mark, marker))
