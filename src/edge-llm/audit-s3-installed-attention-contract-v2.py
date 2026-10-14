"""Read actual source locations, with resumable export links and the compiled operator inspector."""
import hashlib,importlib,json,pathlib
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'S3-installed-attention-contract-v2.json';assert not out.exists()
names=['experimental.builder.ops.functional.attention','experimental.builder.ops.functional._operation',
       'experimental.builder.ops.ragged','experimental.builder.models.qwen3_5.modeling_qwen3_5_text']
rows=[]
for i,name in enumerate(names):
    module=importlib.import_module(name);source=pathlib.Path(module.__file__);data=source.read_bytes()
    link=pathlib.Path('/v2/export')/f'S3-installed-attention-source-{i}.py'
    if link.exists():assert link.resolve()==source.resolve()
    else:link.symlink_to(source)
    rows.append(dict(module=name,path=str(source),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),export=link.name))
inspector=R/'runtime/profiling/attention-fp8-v2/fp16.inspector.json'
link=pathlib.Path('/v2/export')/'S3-attention-fp16-operator-inspector-v2.json';assert not link.exists();link.symlink_to(inspector)
result=dict(status='READ_ONLY_ACTUAL_INSTALLED_ATTENTION_CONTRACT',files=rows,CUDA_calls=False,
    original_locator_error='V1 used experimental.builder.ragged instead of actual experimental.builder.ops.ragged',
    qualified_plugin_not_rebuilt=True,operator_inspector=link.name)
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out)
print(json.dumps(result),flush=True)
