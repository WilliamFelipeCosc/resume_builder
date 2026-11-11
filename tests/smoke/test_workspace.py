"""FND-21/22: workspace imports without touching runtime or private data."""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["resume_core", "resume_api", "resume_worker"])
def test_packages_import_in_empty_directory(name, tmp_path):
    completed = subprocess.run(
        [sys.executable, "-c", f"import {name}"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == ""
    assert list(tmp_path.iterdir()) == []


def test_workspace_dependencies_are_importable():
    for name in ["fastapi", "pydantic", "sqlalchemy", "alembic", "dramatiq", "redis", "structlog"]:
        assert importlib.import_module(name).__name__ == name


def test_pytest_only_collects_project_tests():
    import tomllib

    config = tomllib.loads(Path("pyproject.toml").read_text())
    assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]
