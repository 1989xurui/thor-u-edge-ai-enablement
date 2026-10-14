import pathlib, re, hashlib, json
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
B=pathlib.Path('/mnt/e/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006')
manifests=[B/'03_kernel68/G2_ARTIFACT_SHA256SUMS.txt',B/'03_kernel68/artifacts_g35/G3_5_ARTIFACT_SHA256SUMS.txt']
for d in ['P33_NVGPU_AUDIT_20261008','R4B_61_bootlog_20261008','P39_LIBOS_LOGCHANNEL_20261008']:
    manifests.append(B/'15_g5_openrm'/d/'EVIDENCE_SHA256.txt')
manifests.append(B/'15_g5_openrm/P34_OFF_CLOSURE_20261008/SHA256_MANIFEST.txt')
rows=[]
for m in manifests:
    if not m.exists(): rows.append(dict(manifest=str(m),status='MISSING_MANIFEST')); continue
    for line in m.read_text(errors='replace').splitlines():
        found=re.match(r'^([a-fA-F0-9]{64})\s+\*?(.+?)\s*$',line)
        if not found: continue
        expected,name=found.groups()
        options=[m.parent/name,m.parent/'artifacts'/name,m.parent/pathlib.Path(name).name,B/name.lstrip('./')]
        p=next((p for p in options if p.is_file()),None)
        if p is None:
            rows.append(dict(manifest=str(m),entry=name,status='UNRESOLVED_HISTORICAL_PATH')); continue
        actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
        rows.append(dict(manifest=str(m),path=str(p),expected=expected.lower(),sha256=actual,status='MATCH' if actual==expected.lower() else 'MISMATCH'))
(P/'inputs/evidence-sha-verification.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}))
