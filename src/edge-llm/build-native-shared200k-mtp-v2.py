"""Build one original-checkpoint MTP component; 200K maximum, 64K KV optimum, existing 8K query shapes."""
import argparse,faulthandler,gc,hashlib,importlib.util,inspect,json,pathlib,runpy,sys
import numpy as np
import tensorrt as trt
from tensorrt_edgellm import runtime as n
args=argparse.ArgumentParser();args.add_argument('--role',choices=['base','draft'],required=True);role=args.parse_args().role
faulthandler.enable();assert trt.__version__=='192.0.2.75';native=n.load()
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');M=pathlib.Path('/zeekr_map/nvidia-native-ai-v2');root=M/'engines/native-mtp-shared200k-opt64k-c1'
assert role=='base'
out=R/'S1-shared200k-base-build-v2-result.json';assert not out.exists()and not(root/f'spec_{role}.engine').exists()
admission=json.loads((R/'S1-shared200k-profile-admission.json').read_text());assert admission['shared_max_kv_capacity_tokens']==205824
assert json.loads((R/'S1-verified-private-space-release-result.json').read_text())['status']=='PASS_VERIFIED_PRIVATE_SPACE_RELEASE'
if role=='draft':assert not root.exists();root.mkdir()
else:assert json.loads((R/'S1-shared200k-draft-build-result.json').read_text())['status']=='PASS_SHARED200K_DRAFT_BUILD_ONLY'
selected=json.loads((R/'runtime/config/native-mtp8k-selected-runtime.json').read_text())
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
boundary=load('boundary','/v2/load-fp4-boundary.py').register();bounded=load('bounded_tree','/v2/load-bounded-tree16-state.py').register()
fence=load('fence','/v2/load-trt-stage-fence.py');fence.register()
from experimental.builder.ops.linear import Linear
from experimental.builder.ops import functional as F
from experimental.builder.ops.functional import recurrent as recurrent_ops
from experimental.builder.ops.scope import current_net
from experimental.builder.models.qwen3_5.modeling_qwen3_5_text import Qwen3_5ForCausalLM
from experimental.builder.models.qwen3_5.modeling_qwen3_5_mtp import Qwen35MtpDraftModel
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
    buffers={k:np.array([v],np.int32)for k,v in attrs.items()};fields_list=[trt.PluginField(k,buffers[k],trt.PluginFieldType.INT32)for k in attrs]
    fields=trt.PluginFieldCollection(fields_list);plugin=bounded.create_plugin(name+'.bounded_tree16',fields,trt.TensorRTPhase.BUILD);assert plugin is not None
    retained.append((attrs,buffers,fields_list,fields,plugin));layer=current_net().network.add_plugin_v3([v._as_trt()for v in inputs],[],plugin);assert layer is not None
    counts[name]+=1;return tuple(F.tensor(layer.get_output(i))for i in range(3))
recurrent_ops.operation=operation
original_base=Qwen3_5ForCausalLM.forward;original_draft=Qwen35MtpDraftModel.forward
def forward_base(self,**io):
    marker=io['execution_phase_marker']._as_trt();network=self.ctx.net.network
    io['inputs_embeds']=F.tensor(fence.add(network,[io['inputs_embeds']._as_trt()],marker,0,0)[0]);outputs=original_base(self,**io)
    deps=[v._as_trt()for k,v in outputs.items()if k!='logits'];outputs['logits']=F.tensor(fence.add(network,[outputs['logits']._as_trt()],marker,0,1,deps)[0]);fenced.append(0);return outputs
def forward_draft(self,**io):
    marker=io['execution_phase_marker']._as_trt();network=self.ctx.net.network;keys=['inputs_embeds','base_hidden','draft_hidden']
    began=fence.add(network,[io[k]._as_trt()for k in keys],marker,1,0)
    for key,value in zip(keys,began):io[key]=F.tensor(value)
    outputs=original_draft(self,**io);deps=[v._as_trt()for k,v in outputs.items()if k!='logits']
    outputs['logits']=F.tensor(fence.add(network,[outputs['logits']._as_trt()],marker,1,1,deps)[0]);fenced.append(1);return outputs
Qwen3_5ForCausalLM.forward=forward_base;Qwen35MtpDraftModel.forward=forward_draft
repair=load('mmap_repair','/v2/mmap-checkpoint-weights-v1.py');repair.install()
assert json.loads((R/'S1-mmap-weight-reader-cpu-check.json').read_text())['status']=='PASS_CPU_BYTE_AND_TYPED_EQUIVALENCE_READ_ONLY_MMAP_READER'
from experimental.builder.core import builder
source_path=pathlib.Path(builder.__file__);assert hashlib.sha256(source_path.read_bytes()).hexdigest()=='0dca5a12ca492cd8f40d898ea1e64cf2795db199361b81ea5b7b7627df4aa29e'
profile_source=inspect.getsource(builder._setup_llm_profiles)
old='        set_profile_shapes(name, ragged.fixed_shape(pool_shape))'
assert profile_source.count(old)==1
profile_source=profile_source.replace(old,'        assert pool_pages == 1608 and pages_per_sequence == 1608\n        pool_shapes = tuple((2, pages, page_size, layer_heads, layer_dim) for pages in (70, 520, 1608))\n        set_profile_shapes(name, pool_shapes)')
start=profile_source.index('    page_shapes = ((1, 2, pages_per_sequence)');end=profile_source.index('    set_profile_shapes("kv_page_table", page_shapes)',start)
profile_source=profile_source[:start]+'    assert max_sequences == 1\n    page_shapes = ((1, 2, 70), (1, 2, 520), (1, 2, 1608))\n'+profile_source[end:]
exec(compile(profile_source,__file__+'::dynamic_kv_min8_opt64_max200','exec'),builder.__dict__)
from experimental.builder import cli
original_plan=cli._build_plan
def selected_component(args,bundle,components):
    plans=original_plan(args,bundle,components);assert[p[0]for p in plans]==['spec-base','spec-draft']
    return [plans[0 if role=='base'else 1]]
cli._build_plan=selected_component
sys.argv=['edge-stream-build.py','--model-dir',selected['checkpoint_dir'],'--engine-dir',str(root),'--components','llm','--max-input-len','8448','--max-kv-cache-capacity','205824','--max-batch-size','1','--spec-type','mtp','--tree-base','--max-verify-tree-size','16','--max-draft-tree-size','16']
print(json.dumps(dict(stage='BUILD_SHARED200K_COMPONENT',role=role,KV_pages_min_opt_max=[70,520,1608],prefill_max=8448,weights_unchanged=True)),flush=True)
runpy.run_path('/v2/edge-stream-build-mmap-v2.py',run_name='__main__')
assert fenced==[0 if role=='base'else 1]
assert counts==({'gated_delta_net':48,'causal_conv1d':48}if role=='base'else{'gated_delta_net':0,'causal_conv1d':0})
assert len(changed)==(192 if role=='base'else 0)
config=json.loads((root/f'{role}_config.json').read_text());bc=config['builder_config']
assert bc['max_kv_cache_capacity']==205824 and bc['max_kv_pool_pages']==1608 and bc['max_input_len']==8448
engine=root/f'spec_{role}.engine';size=engine.stat().st_size
assert (16*1024**3<size<18*1024**3)if role=='base'else(512*1024**2<size<1024**3)
with engine.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
result=dict(status='PASS_SHARED200K_'+role.upper()+'_BUILD_ONLY',engine_dir=str(root),role=role,engine_bytes=size,engine_sha256=sha,config=config,KV_profile_pages_min_opt_max=[70,520,1608],profile_adapter_sha256=hashlib.sha256(profile_source.encode()).hexdigest(),mmap_reader_stats=repair.stats,reader_CPU_equivalence='S1-mmap-weight-reader-cpu-check.json',original_Draft_reused=True,Golden_changed=False,actual_inference_pass=False,performance_admitted=False,source_checkpoint=selected['checkpoint_dir'])
out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='config'}),flush=True)
