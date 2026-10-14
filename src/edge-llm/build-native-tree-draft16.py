"""Repair observed accept-step [9,5120] overflow; compile only original-checkpoint MTP draft."""
import faulthandler,hashlib,importlib.util,json,os,pathlib,runpy,sys
import tensorrt as trt
faulthandler.enable();assert trt.__version__=='192.0.2.75'
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');M=pathlib.Path('/zeekr_map/nvidia-native-ai-v2')
out=R/'native-tree-draft16-build-result.json';root=M/'diagnostics/native-tree-draft16-c1-8k';pair=R/'diagnostics/native-tree-mini4-draft16-c1-8k'
assert not out.exists()and not root.exists()and not pair.exists()
failed=json.loads((R/'native-tree-mini4-execution-v2-result.json').read_text());assert failed['status']=='FAIL_INSTALLED_NATIVE_TREE_MINI4'and len(failed['cases'])==1
log=(R/'logs/native-tree-mini4-v3.log').read_text();assert 'Supplied binding dimensions [9,5120]'in log and '[8,5120]'in log
prior=json.loads((R/'native-tree-mini4-build-result.json').read_text());assert prior['status']=='PASS_TREE_MINI4_TARGET_BUILD_AND_K7_DRAFT_HARDLINK_ONLY'
source=pathlib.Path(prior['engine_dir']);base=source/'spec_base.engine';before=base.stat();assert before.st_size==1773112524
selected=json.loads((R/'runtime/config/native-mtp8k-selected-runtime.json').read_text());assert selected['MTP_K']==7
root.mkdir(parents=True)
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fence=load('fence','/v2/load-trt-stage-fence.py');fence.register()
from experimental.builder.models.qwen3_5.modeling_qwen3_5_mtp import Qwen35MtpDraftModel
from experimental.builder.ops import functional as F
original=Qwen35MtpDraftModel.forward;fenced=[]
def forward(self,**io):
    marker=io['execution_phase_marker']._as_trt();net=self.ctx.net.network;keys=['inputs_embeds','base_hidden','draft_hidden']
    began=fence.add(net,[io[k]._as_trt()for k in keys],marker,1,0)
    for k,v in zip(keys,began):io[k]=F.tensor(v)
    outputs=original(self,**io);deps=[v._as_trt()for k,v in outputs.items()if k!='logits']
    outputs['logits']=F.tensor(fence.add(net,[outputs['logits']._as_trt()],marker,1,1,deps)[0]);fenced.append(1);return outputs
Qwen35MtpDraftModel.forward=forward
from experimental.builder import cli
original_plan=cli._build_plan
def draft_only(args,bundle,components):
    plans=original_plan(args,bundle,components);assert[p[0]for p in plans]==['spec-base','spec-draft']and plans[1][1].spec_role=='draft'
    return plans[1:]
cli._build_plan=draft_only
sys.argv=['edge-stream-build.py','--model-dir',selected['checkpoint_dir'],'--engine-dir',str(root),'--components','llm',
    '--max-input-len','8448','--max-kv-cache-capacity','8960','--max-batch-size','1','--spec-type','mtp','--max-verify-tree-size','16','--max-draft-tree-size','16']
print(json.dumps(dict(stage='BUILD_MTP_DRAFT_PROFILE16_ONLY',target_recompiled=False,observed_failure='Accept-step9 exceeds profile8',draft_source='Original same-checkpoint MTP FP16')),flush=True)
runpy.run_path('/v2/edge-stream-build.py',run_name='__main__');assert fenced==[1]and not(root/'spec_base.engine').exists()
draft=root/'spec_draft.engine';cfg=json.loads((root/'draft_config.json').read_text());assert cfg['builder_config']['max_draft_tree_size']==16 and cfg['num_hidden_layers']==1
assert 512*1024**2<draft.stat().st_size<1024**3
pair.mkdir()
for p in source.iterdir():
    if p.name not in('spec_draft.engine','draft_config.json')and p.is_file():os.link(p,pair/p.name)
os.symlink(draft,pair/'spec_draft.engine');os.symlink(root/'draft_config.json',pair/'draft_config.json')
after=base.stat();linked=(pair/'spec_base.engine').stat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
assert(before.st_dev,before.st_ino)==(linked.st_dev,linked.st_ino)
v=dict(status='PASS_ORIGINAL_MTP_DRAFT16_AND_REUSED_TREE_MINI4_TARGET_BUILD_ONLY',engine_dir=str(pair),draft_engine_dir=str(root),
    draft_engine_bytes=draft.stat().st_size,draft_engine_sha256=hashlib.file_digest(draft.open('rb'),'sha256').hexdigest(),draft_config=cfg,
    base_engine_bytes=before.st_size,base_engine_sha256=prior['base_engine_sha256'],target_recompiled=False,
    target_reuse='Unchanged same-filesystem hardlink/inode/size/mtime;previous SHA reused',
    checkpoint=selected['checkpoint_dir'],new_checkpoint_downloaded=False,whole27B=False,actual_executed_8K=False,
    observed_required_draft_positions=9,draft_profile_capacity=16,vanilla_oracle_reused_without_execute=True)
out.write_text(json.dumps(v,indent=2));os.sync();print(json.dumps({k:v[k]for k in('status','draft_engine_bytes','draft_engine_sha256','target_recompiled')}),flush=True)
