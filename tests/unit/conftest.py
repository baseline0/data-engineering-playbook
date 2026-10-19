"""Unit test configuration.

Every test under tests/unit/ gets the `unit` marker at collection time, so
`pytest -m unit` selects this folder. Unit tests are deterministic and need no
external services, network access, or sibling repos.
"""

from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "unit: deterministic, isolated, no external dependencies"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark every collected test that lives under tests/unit/."""
    unit_dir = Path(config.rootpath, "tests", "unit")
    for item in items:
        if Path(item.path).is_relative_to(unit_dir):
            item.add_marker(pytest.mark.unit)
