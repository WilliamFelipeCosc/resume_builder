"""Dependency logs are confined to sanitized stderr in a real process."""

import os
import subprocess
import sys


def test_dependency_logs_do_not_contaminate_protocol_stdout(tmp_path):
    code = """
import logging
from resume_core.logging_policy import configure_mcp_logging
configure_mcp_logging()
logging.getLogger("fastmcp").warning("dependency-sentinel")
print("protocol-frame")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == "protocol-frame\n"
    assert '"event": "dependency_event"' in result.stderr
    assert "dependency-sentinel" not in result.stderr


def test_reconfigured_dependency_handler_cannot_bypass_policy(tmp_path):
    code = """
import logging
import fastmcp
from resume_core.logging_policy import configure_mcp_logging
logging.getLogger("fastmcp").addHandler(logging.StreamHandler())
configure_mcp_logging()
logging.getLogger("fastmcp").error("handler-sentinel")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    assert '"event": "dependency_event"' in result.stderr
    assert "handler-sentinel" not in result.stderr
