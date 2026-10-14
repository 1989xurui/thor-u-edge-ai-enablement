"""Identify Target versus MTP attention prefixes from actual metadata, without GPU or weight reads."""
import inspect,json,pathlib,re
from experimental.builder.core.weights import Weights
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'S3-KV-prefixes-audit-v1.json';assert not out.exists()
build=json.loads((R/'S2-dflash2-shared200k-base-build-v1-result.json').read_text())
model=pathlib.Path(build['source_checkpoint']);path=model/'model.safetensors.index.json'
mapping=json.loads(path.read_text())['weight_map']
prefixes=sorted({n.split('.q_proj.')[0]for n in mapping if '.self_attn.q_proj.'in n})
grouped={}
for prefix in prefixes:
    group='MTP'if re.search(r'(?:^|\.)mtp(?:\.|$)',prefix)else'Target_or_other'
    grouped.setdefault(group,[]).append(prefix)
result=dict(status='READ_ONLY_ACTUAL_TARGET_MTP_PREFIX_AUDIT',q_proj_prefixes=prefixes,grouped=grouped,
    explicit_Target_layers=build['config']['num_hidden_layers'],Target_attention_layers=build['config']['num_attention_layers'],
    attention_key_samples=[n for n in mapping if '.self_attn.'in n][:24],
    installed_scale_recipe=inspect.getsource(Weights.qkv_scales),CUDA_calls=False,model_weights_loaded=False)
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out)
link=pathlib.Path('/v2/export')/'S3-checkpoint-weight-index.json';assert not link.exists();link.symlink_to(path)
print(json.dumps(dict(status=result['status'],prefix_count=len(prefixes),groups={k:len(v)for k,v in grouped.items()})),flush=True)
