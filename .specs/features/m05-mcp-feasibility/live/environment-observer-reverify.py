import json,pathlib,time
r=pathlib.Path('/tmp/rb-m05-reverify-20261116')
allowed={'HOME','XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','PATH','LANG'}
end=time.monotonic()+300
while time.monotonic()<end:
 try:
  p=json.loads((r/'marker.json').read_text()); pid=int(p['pid']); d=pathlib.Path('/proc')/str(pid)
  if b'resume_mcp_server' not in (d/'cmdline').read_bytes().split(b'\0'):
   time.sleep(.02); continue
  keys={x.partition(b'=')[0].decode(errors='replace') for x in (d/'environ').read_bytes().split(b'\0') if x}
  result={'pid':pid,'sentinel_before':p['sentinel_before'],'sentinel_after':'M05_SYNTHETIC_SENTINEL' in keys,'only_allowlisted_keys':keys<=allowed,'allowed_keys_count':len(keys)}
  (r/'observed.json').write_text(json.dumps(result)); print(json.dumps(result),flush=True); break
 except (OSError,ValueError,KeyError): pass
 time.sleep(.02)
else: raise SystemExit('observation timeout')
