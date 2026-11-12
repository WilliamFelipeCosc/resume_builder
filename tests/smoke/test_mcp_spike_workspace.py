import importlib.metadata
import os
import subprocess
import sys


def test_spike_imports_have_no_observable_side_effects(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "import resume_core; import resume_mcp_server"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_fastmcp_version_is_pinned():
    assert importlib.metadata.version("fastmcp") == "4.1.8"


def test_mcp_sdk_version_is_pinned():
    assert importlib.metadata.version("mcp") == "2.3.0"
