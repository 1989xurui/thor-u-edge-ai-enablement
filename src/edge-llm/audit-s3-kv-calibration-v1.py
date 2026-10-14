"""Read checkpoint metadata and the installed scale-loading recipe; no model weight loads or CUDA calls."""
import hashlib,inspect,json,pathlib,re
from experimental.builder import ops
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'S3-KV-calibration-audit-v1.json';assert not out.exists()
build=json.loads((R/'S2-dflash2-shared200k-base-build-v1-result.json').read_text())
model=pathlib.Path(build['source_checkpoint']);index_path=model/'model.safetensors.index.json'
index=json.loads(index_path.read_text());keys=list(index['weight_map'])
scale_keys=[name for name in keys if re.search(r'(?:^|\.)(?:[qkv]_cache_scale|kv_cache_scale|[qkv]_scale)(?:\.|$)',name)]
output_scales=[name for name in keys if name.endswith('.output_scale')]
configs=[]
for name in ['config.json','hf_quant_config.json','quantization_config.json']:
    path=model/name
    if path.exists():
        data=path.read_bytes();value=json.loads(data)
        configs.append(dict(name=name,sha256=hashlib.sha256(data).hexdigest(),
            quantization=value.get('quantization',value.get('quantization_config',value))))
source=pathlib.Path(inspect.getfile(ops.GatedDecoderAttention))
link=pathlib.Path('/v2/export')/'S3-installed-GatedDecoderAttention.py';assert not link.exists();link.symlink_to(source)
result=dict(status='READ_ONLY_CHECKPOINT_KV_CALIBRATION_METADATA',checkpoint=str(model),
    checkpoint_revision='fed99d815f4e8c7c616dd3dd6780076e26d5fb61',
    index_sha256=hashlib.sha256(index_path.read_bytes()).hexdigest(),tensor_count=len(keys),
    explicit_cache_or_qkv_scale_names=scale_keys,output_scale_names=output_scales,configs=configs,
    installed_scale_recipe=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),export=link.name),
    model_weights_loaded=False,CUDA_calls=False,FP8_full_model_calibration_PASS=False,
    interpretation='Metadata presence alone is not full-model FP8 quality acceptance;inspect installed recipe and actual scale values before promotion')
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out)
print(json.dumps(dict(status=result['status'],explicit_scales=len(scale_keys),output_scales=len(output_scales),recipe=link.name)),flush=True)
