import json,os,pathlib
p=pathlib.Path('/tmp/rb-m05-reverify-20261116/marker.json')
p.write_text(json.dumps({'pid':os.getpid(),'sentinel_before':'M05_SYNTHETIC_SENTINEL' in os.environ}))
os.chmod(p,0o600)
os.execv('/home/williamf/projects/resume_builder/tools/mcp-spike-launch',['mcp-spike-launch','hermes'])
