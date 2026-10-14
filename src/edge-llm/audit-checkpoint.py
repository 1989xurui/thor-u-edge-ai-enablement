import pathlib,json,hashlib,struct,urllib.request,collections,datetime,sys
P=pathlib.Path(r'D:\Thor64G\THOR_NVIDIA_NVFP4_20261013');M=pathlib.Path(r'E:\Thor64G_AI\ModelStore\Qwen3.8-27B_2026-09-09\nvidia_Qwen3.8-27B-NVFP4_fed99d')
REV='fed99d815f4e8c7c616dd3dd6780076e26d5fb61'
def save(n,d):(P/'evidence'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
c=load(M/'config.json');q=load(M/'hf_quant_config.json');index=load(M/'model.safetensors.index.json')
metadata=json.load(urllib.request.urlopen('https://huggingface.co/api/models/nvidia/Qwen3.8-27B-NVFP4/revision/'+REV+'?blobs=true',timeout=45))
assert metadata['sha']==REV
official={x['rfilename']:x for x in metadata['siblings']};save('hf-pinned-metadata.json',metadata)
layers=q['quantization']['quantized_layers'];records=[];all_tensors={};expected_shards=sorted(set(index['weight_map'].values()))
for name in expected_shards:
 f=M/name;st=f.stat();entry=official[name];expected=entry['lfs']['sha256'];assert st.st_size==entry['lfs']['size']
 with f.open('rb') as h:
  length=struct.unpack('<Q',h.read(8))[0];assert length<16*1024*1024;header=json.loads(h.read(length))
  for k,v in header.items():
   if k=='__metadata__':continue
   assert v['data_offsets'][0]<=v['data_offsets'][1]<=st.st_size-8-length
   assert index['weight_map'][k]==name;all_tensors[k]=dict(v,shard=name)
 save('checkpoint-header-index.json',all_tensors)
 save('checkpoint-progress.json',dict(phase='HASHING_READ_ONLY_E',current=name,completed=len(records)))
 sha=hashlib.sha256();n=0
 with f.open('rb') as h:
  while chunk:=h.read(16*1024*1024):
   sha.update(chunk);n+=len(chunk)
   if n%(512*1024*1024)==0:save('checkpoint-progress.json',dict(phase='HASHING_READ_ONLY_E',current=name,read_bytes=n,total=st.st_size,completed=len(records)))
 actual=sha.hexdigest();assert actual==expected,(name,actual,expected);assert f.stat().st_mtime_ns==st.st_mtime_ns
 records.append(dict(name=name,size=st.st_size,sha256=actual,official_sha_match=True,header_tensors=len(header)-int('__metadata__' in header)))
 print(json.dumps(dict(shard=name,sha_match=True,bytes=st.st_size)),flush=True)
assert set(index['weight_map'])==set(all_tensors)
summary=dict(model_id='nvidia/Qwen3.8-27B-NVFP4',revision=REV,source=str(M),architecture=c['architectures'],model_type=c['model_type'],text_config=c['text_config'],vision_config=c['vision_config'],quant_algo=q['quantization']['quant_algo'],modelopt=q['producer'],quantized_layer_count=len(layers),quant_counts=dict(collections.Counter(v['quant_algo']for v in layers.values())),dtypes=dict(collections.Counter(v['dtype']for v in all_tensors.values())),tensor_count=len(all_tensors),shards=records,total_bytes=sum(r['size']for r in records),read_errors=0,copy_performed=False,quantized_layers=layers,mtp_tensor_count=sum(k.startswith('mtp.')or'.mtp.'in k for k in all_tensors),small_files=[dict(name=f.name,size=f.stat().st_size,sha256=hashlib.file_digest(f.open('rb'),'sha256').hexdigest())for f in M.iterdir()if f.is_file()and not f.name.endswith('.safetensors')],status='PASS_IDENTITY_AND_READ_INTEGRITY_NOT_ENGINE_COMPATIBILITY')
save('checkpoint-audit.json',summary);save('checkpoint-progress.json',dict(phase='COMPLETE',shards=len(records),status=summary['status']));print(json.dumps({k:summary[k]for k in ['status','tensor_count','quantized_layer_count','quant_counts','dtypes','total_bytes','mtp_tensor_count']}))
