import pathlib,json
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
current=json.loads((P/'logs/vehicle-root-preflight.json').read_text())['firmware']
candidate=json.loads((P/'logs/static-contract.json').read_text())['firmware']
def key(p):return '/'.join(p.split('/')[-2:])
rows=[]
for c in candidate:
    matches=[r for r in current if key(r['path'])==key(c['path'])]
    rows.append(dict(candidate=c['path'],candidate_sha256=c['sha256'],current=matches,status='MATCH_CURRENT_DRIVE_BYTES' if any(r['sha256']==c['sha256'] for r in matches) else ('DIFFERENT' if matches else 'MISSING_CURRENT')))
(P/'logs/live-firmware-comparison.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}))
