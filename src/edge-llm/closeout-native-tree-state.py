"""Seal isolated native Tree-state evidence; leave complete Tree runtime NO-GO."""
import csv,datetime,hashlib,json,pathlib,shutil,urllib.request
P=pathlib.Path(__file__).resolve().parents[1];E=P/'evidence';A=P/'artifacts'
def read(n):return json.loads((E/n).read_text(encoding='utf-8'))
def digest(p):
    d=p.read_bytes();return dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
run=read('native-tree-state-v2-result.json');decision=read('native-tree-state-decision.json');guard=read('native-tree-state-v2-guard-result.json')
assert run['status']=='PASS_NATIVE_TREE16_GDN_CONV_OBSERVED_STATE_HANDOFF_AND_RESUME_COMPONENTS_ONLY' and guard['returncode']==0
assert run['full27B_Tree_MTP']=='NOT_TESTED' and decision['native_wheel_acceptance'].startswith('NOT_INVOKED')
selected=read('native-mtp8k-selected-runtime.json');assert selected['MTP_K']==7 and selected['verify_positions']==8
assert selected['next_unique_action']==decision['next_unique_action']
with urllib.request.urlopen('http://192.0.2.222:8003/native-mtp8k-selected-runtime.json',timeout=10)as r:remote=r.read(65537)
assert remote==(E/'native-mtp8k-selected-runtime.json').read_bytes()==(A/'native-mtp8k-selected-runtime.json').read_bytes()
for name,sha in(('native-tree-state-gdn.engine',run['cases'][0]['plan']['sha256']),('native-tree-state-conv.engine',run['cases'][1]['plan']['sha256']),('native-tree-replay-v1.cubin',decision['replay_cubin_sha256'])):
    with urllib.request.urlopen('http://192.0.2.222:8003/'+name,timeout=10)as r:data=r.read(1024**2)
    assert hashlib.sha256(data).hexdigest()==sha;(A/name).write_bytes(data)
live=read('mtp-live-observation.json');raw=read('native-job-observation.json')
assert live['fresh_process_observation'] and live['jobs']==[] and raw['active_jobs']==[]
assert live['boot_id']=='9d74daba-0347-489c-9192-2d117806cbe7' and live['Tj_C']<95 and min(live['DATA_free_GiB'],live['MAP_free_GiB'])>=12
with (P/'COMPONENT_MATRIX.csv').open(encoding='utf-8-sig',newline='')as f:rows=list(csv.DictReader(f))
assert len(rows)==128
names=('native-tree-state-result.json','native-tree-state-guard-result.json','native-tree-state.log','native-tree-state-graph-nodes.jsonl',
       'native-tree-state-v2-result.json','native-tree-state-v2-guard-result.json','native-tree-state-v2.log','native-tree-state-v2-graph-nodes.jsonl',
       'native-tree-replay-build-result.json','native-tree-replay-compile.log','native-tree-replay-source.json','native-tree-state-decision.json','native-mtp8k-selected-runtime.json','native-job-observation.json')
scripts=('probe-native-tree-state.py','load-native-tree-replay.py','native-tree-replay-v1.cu','prepare-native-tree-replay.py',
         'package-native-tree-state.py','guard-native-tree-state-v2.py','finalize-native-tree-state.py','update-deliverables.py')
receipt=dict(status='PASS_NATIVE_TREE16_STATE_COMPONENTS_RECEIPTS_AND_CURRENT_SELECTION_CLOSEOUT',timestamp=datetime.datetime.now().astimezone().isoformat(),
    files={n:digest(E/n)for n in names},scripts={n:digest(P/'scripts'/n)for n in scripts},
    component_artifacts={n:digest(A/n)for n in('native-tree-state-gdn.engine','native-tree-state-conv.engine','native-tree-replay-v1.cubin')},
    report=digest(P/'TOTAL_REPORT.md'),matrix=digest(P/'COMPONENT_MATRIX.csv'),matrix_rows=len(rows),live=live,D_free_bytes=shutil.disk_usage(P).free,
    GDN_and_Conv_state_components='GO_SCOPED_SYNTHETIC_OPERATOR_AND_NATIVE_RESUME_ONLY',
    Tree_full_runtime='NO_GO_ENGINE_PROFILE8_AND_TREE_PREFILL_ALLOCATION_NOT_ADMITTED',
    current_K7_retained=True,E_read_only=True,full_platform='NO_GO_PENDING_OTHER_GATES',next_unique_action=decision['next_unique_action'])
assert receipt['D_free_bytes']>=10*1024**3
(E/'native-tree-state-closeout-integrity.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({k:receipt[k]for k in('status','matrix_rows','D_free_bytes','Tree_full_runtime','next_unique_action')}))
