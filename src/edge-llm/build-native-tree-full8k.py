"""One full64-layer Tree target; retain selected K7 and reuse repaired same-checkpoint draft16."""
import faulthandler,hashlib,importlib.util,json,os,pathlib,runpy,shutil,sys
import numpy as np
import tensorrt as trt
from tensorrt_edgellm import runtime as n
faulthandler.enable();assert trt.__version__=='192.0.2.75';native=n.load()
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');M=pathlib.Path('/zeekr_map/nvidia-native-ai-v2');root=M/'engines/native-tree-mtp8-top2-node16-c1-8k'
out=R/'native-tree-full8k-build-result.json';assert not out.exists()and not root.exists()
assert json.loads((R/'native-tree-full-space-preparation.json').read_text())['status']=='PASS_ARCHIVED_FALLBACK_AND_RECLAIMED_EXACT_MAP_PLAN'
assert json.loads((R/'native-tree-mini4-execution-v3-result.json').read_text())['status']=='PASS_INSTALLED_NATIVE_TREE_MINI4_GREEDY_ACCEPT_COMMIT_AND_CONTINUATION_ONLY'
repair=json.loads((R/'native-tree-draft16-build-result.json').read_text());assert repair['status']=='PASS_ORIGINAL_MTP_DRAFT16_AND_REUSED_TREE_MINI4_TARGET_BUILD_ONLY'
root.mkdir()
prior=json.loads((R/'native-tree-bounded16-load-v2-result.json').read_text())
assert prior['status']=='PASS_BOUNDED_TREE16_FRESH_DESERIALIZATION_CAPPED_PREFILL_AND_STATE_FLOW_ONLY'
selected=json.loads((R/'runtime/config/native-mtp8k-selected-runtime.json').read_text());assert selected['MTP_K']==7
source=pathlib.Path(repair['draft_engine_dir']);draft=source/'spec_draft.engine';before=draft.stat()
draft_config=json.loads((source/'draft_config.json').read_text());assert before.st_size==718719228 and draft_config['builder_config']['max_draft_tree_size']==16

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
boundary=load('boundary','/v2/load-fp4-boundary.py').register()
bounded=load('bounded_tree','/v2/load-bounded-tree16-state.py').register()
fence=load('fence','/v2/load-trt-stage-fence.py');fence.register()
from experimental.builder.ops.linear import Linear
from experimental.builder.ops import functional as F
from experimental.builder.ops.functional import recurrent as recurrent_ops
from experimental.builder.ops.scope import current_net
from experimental.builder.models.qwen3_5.modeling_qwen3_5_text import Qwen3_5ForCausalLM
original_linear=Linear.forward;original_operation=recurrent_ops.operation;retained=[];changed=set();counts={'gated_delta_net':0,'causal_conv1d':0};fenced=[]

def linear(self,hidden_states,rank=None):
    if '.mlp.'not in self.prefix or self.quant_type()!='nvfp4':return original_linear(self,hidden_states,rank)
    assert self.cfg.tp_size==1 and not self.has_adapter()and not self._uses_lora()
    plugin=boundary.create_plugin(self.prefix+'.fp4_input_boundary',trt.PluginFieldCollection([]),trt.TensorRTPhase.BUILD)
    layer=self.ctx.net.network.add_plugin_v3([hidden_states._as_trt()],[],plugin);assert layer is not None
    changed.add(self.prefix);return original_linear(self,F.tensor(layer.get_output(0)),rank)
Linear.forward=linear

def operation(name,inputs,*,output_count=1,**attrs):
    if name not in counts:return original_operation(name,inputs,output_count=output_count,**attrs)
    assert output_count==3 and attrs['use_ddtree']==1 and attrs['use_mtp']==0 and not attrs.get('use_diffusion_state')
    attrs=dict(attrs,thor_delegate_kind=0 if name=='gated_delta_net'else 1,thor_snapshot_cap=16)
    buffers={k:np.array([v],np.int32)for k,v in attrs.items()}
    fields_list=[trt.PluginField(k,buffers[k],trt.PluginFieldType.INT32)for k in attrs];fields=trt.PluginFieldCollection(fields_list)
    plugin=bounded.create_plugin(name+'.bounded_tree16',fields,trt.TensorRTPhase.BUILD);assert plugin is not None
    retained.append((attrs,buffers,fields_list,fields,plugin))
    layer=current_net().network.add_plugin_v3([v._as_trt()for v in inputs],[],plugin);assert layer is not None
    counts[name]+=1;return tuple(F.tensor(layer.get_output(i))for i in range(3))
recurrent_ops.operation=operation
original_forward=Qwen3_5ForCausalLM.forward

def forward(self,**io):
    marker=io['execution_phase_marker']._as_trt();network=self.ctx.net.network
    io['inputs_embeds']=F.tensor(fence.add(network,[io['inputs_embeds']._as_trt()],marker,0,0)[0])
    outputs=original_forward(self,**io);deps=[v._as_trt()for k,v in outputs.items()if k!='logits']
    outputs['logits']=F.tensor(fence.add(network,[outputs['logits']._as_trt()],marker,0,1,deps)[0]);fenced.append(0);return outputs
Qwen3_5ForCausalLM.forward=forward
from experimental.builder import cli
original_plan=cli._build_plan

def base_only(args,bundle,components):
    plans=original_plan(args,bundle,components);assert[p[0]for p in plans]==['spec-base','spec-draft']and plans[0][1].tree_base
    return plans[:1]
cli._build_plan=base_only
sys.argv=['edge-stream-build.py','--model-dir',selected['checkpoint_dir'],'--engine-dir',str(root),'--components','llm',
    '--max-input-len','8448','--max-kv-cache-capacity','8960','--max-batch-size','1',
    '--spec-type','mtp','--tree-base','--max-verify-tree-size','16','--max-draft-tree-size','16']
print(json.dumps(dict(stage='BUILD_FULL27B_TREE_TARGET_ONLY',engine_dir=str(root),draft_recompiled=False,weights_unchanged=True)),flush=True)
runpy.run_path('/v2/edge-stream-build.py',run_name='__main__')
assert len(changed)==192 and counts=={'gated_delta_net':48,'causal_conv1d':48}and fenced==[0]
assert not(root/'spec_draft.engine').exists();os.link(draft,root/'spec_draft.engine');shutil.copyfile(source/'draft_config.json',root/'draft_config.json')
after=draft.stat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
cfg=json.loads((root/'base_config.json').read_text());assert cfg['builder_config']['max_verify_tree_size']==16
assert cfg['mtp_tree_base']and cfg['num_hidden_layers']==64 and cfg['num_linear_attn_layers']==48 and cfg['num_attention_layers']==16,cfg
base=root/'spec_base.engine';assert 16*1024**3<base.stat().st_size<20*1024**3
v=dict(status='PASS_FULL27B_TREE_TARGET_BUILD_AND_UNCHANGED_DRAFT16_HARDLINK_ONLY',engine_dir=str(root),base_engine_bytes=base.stat().st_size,
    base_engine_sha256=hashlib.file_digest(base.open('rb'),'sha256').hexdigest(),base_config=cfg,
    draft_source=str(draft),draft_engine_bytes=before.st_size,draft_engine_sha256=repair['draft_engine_sha256'],
    draft_stat=dict(device=before.st_dev,inode=before.st_ino,mtime_ns=before.st_mtime_ns),draft_recompiled=False,draft_config=draft_config,
    draft_SHA_scope='Previously verified selected draft;hardlink inode/size/mtime equivalence;not rehashed',
    bounded_tree_layers=counts,MLP_FP4_boundaries=len(changed),actual_executed_8K=False,whole27B=True,quality_acceptance=False,default_K7_changed=False)
out.write_text(json.dumps(v,indent=2));os.sync();print(json.dumps(dict(status=v['status'],base_engine_bytes=v['base_engine_bytes'],base_engine_sha256=v['base_engine_sha256'])),flush=True)
