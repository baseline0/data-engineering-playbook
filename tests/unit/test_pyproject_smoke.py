"""Smoke test: pyproject.toml parses and declares a project name. Placeholder until real unit tests exist."""

import tomllib
from pathlib import Path


def test_pyproject_declares_a_project_name() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["name"]
