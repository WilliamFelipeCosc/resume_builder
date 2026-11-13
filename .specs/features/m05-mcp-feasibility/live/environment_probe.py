#!/usr/bin/env python3
"""Write only a synthetic sentinel presence bit before exec of the real launcher."""
import json
import os
import pathlib
import sys

profile = sys.argv[1]
assert profile in ("hermes", "codex")
marker = pathlib.Path('/tmp/rb-m05-live-w5Pcw6') / f'env-probe-{profile}.json'
marker.write_text(json.dumps({"pid": os.getpid(), "sentinel_before": "M05_SYNTHETIC_SENTINEL" in os.environ}))
os.chmod(marker, 0o600)
os.execv('/home/williamf/projects/resume_builder/tools/mcp-spike-launch', ['mcp-spike-launch', profile])
