import pathlib,sys,json,collections,os,inspect,dataclasses
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME='/work/native-v2/cache',TOKENIZERS_PARALLELISM='false',USE_TORCH='0')
sys.path.insert(0,'/work/native-v2/edge')
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');M=pathlib.Path('/mnt/e/Thor64G_AI/ModelStore/Qwen3.8-27B_2026-09-09/nvidia_Qwen3.8-27B-NVFP4_fed99d')
from tensorrt_edgellm.config import ModelConfig
from experimental.builder.core.config import DeviceConfig
out=dict(source_commit='95515c2f87fba8982db5a519f9022277667b3cc9',release='0.11.0',checkpoint_mutated=False,full_model_loaded=False)
for name,fn,args in [('exporter_config',ModelConfig.from_pretrained,dict(model_dir=str(M),default_attention_scale=lambda dim:dim**-0.5)),('direct_builder_config',DeviceConfig.from_pretrained,dict(model_dir=str(M)))]:
 try:
  obj=fn(**args);d=dataclasses.asdict(obj);(P/'evidence'/('edge-'+name+'.json')).write_text(json.dumps(d,indent=2,default=str));out[name]=dict(status='PASS_SCHEMA_PARSE_ONLY',fields=list(d),layer_counts=dict(collections.Counter(d.get('layer_types',[]))),quant=d.get('quant'),model_type=d.get('model_type'))
 except Exception as e:out[name]=dict(status='FAIL',error=repr(e),signature=str(inspect.signature(fn)))
(P/'evidence/edge-schema-admission.json').write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({name:{k:v for k,v in data.items()if k in ['status','error','signature','layer_counts','model_type']}for name,data in out.items()if isinstance(data,dict)}))
