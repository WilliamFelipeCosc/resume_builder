#!/usr/bin/env python3
"""Observe the launcher PID after exec; never print environment values."""
import json
import pathlib
import sys
import time

profile = sys.argv[1]
assert profile in ("hermes", "codex")
root = pathlib.Path('/tmp/rb-m05-live-w5Pcw6')
marker = root / f'env-probe-{profile}.json'
out = root / f'env-observed-{profile}.json'
deadline = time.monotonic() + 180
allowed = {'HOME', 'XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME', 'PATH', 'LANG'}
while time.monotonic() < deadline:
    try:
        pre = json.loads(marker.read_text())
        pid = int(pre['pid'])
        proc = pathlib.Path('/proc') / str(pid)
        cmd = (proc / 'cmdline').read_bytes().split(b'\0')
        if b'resume_mcp_server' not in cmd or profile.encode() not in cmd:
            time.sleep(.02)
            continue
        keys = {part.partition(b'=')[0].decode('utf-8', 'replace') for part in (proc / 'environ').read_bytes().split(b'\0') if part}
        result = {'sentinel_before': pre['sentinel_before'], 'sentinel_after': 'M05_SYNTHETIC_SENTINEL' in keys, 'only_allowlisted_keys': keys <= allowed, 'allowed_keys_count': len(keys), 'process_identified': True}
        out.write_text(json.dumps(result))
        print(json.dumps(result), flush=True)
        sys.exit(0 if result['sentinel_before'] and not result['sentinel_after'] and result['only_allowlisted_keys'] else 1)
    except (FileNotFoundError, ProcessLookupError, PermissionError, json.JSONDecodeError):
        pass
    time.sleep(.02)
print('Observation timed out without a matching MCP process', file=sys.stderr)
sys.exit(1)
