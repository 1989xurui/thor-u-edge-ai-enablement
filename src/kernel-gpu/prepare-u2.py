import pathlib,json,urllib.request,hashlib,tarfile,concurrent.futures
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013');W=pathlib.Path('/work/a1/cuda-u2');W.mkdir(exist_ok=True)
url='https://developer.download.nvidia.com/compute/cuda/redist/'
manifest=json.load(urllib.request.urlopen(url+'redistrib_13.2.2.json',timeout=30));(P/'inputs/cuda-u2-manifest.json').write_text(json.dumps(manifest,indent=2))
items=[('cuda_nvcc','linux-x86_64'),('libnvvm','linux-x86_64'),('cuda_cudart','linux-x86_64'),('cuda_cccl','linux-x86_64'),('cuda_crt','linux-x86_64'),('cuda_cudart','linux-sbsa')]
def fetch(pair):
    component,arch=pair;entry=manifest[component][arch];p=W/pathlib.Path(entry['relative_path']).name
    if not p.exists() or hashlib.file_digest(p.open('rb'),'sha256').hexdigest()!=entry['sha256']:
        urllib.request.urlretrieve(url+entry['relative_path'],p)
    sha=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha==entry['sha256']
    dest=W/arch;dest.mkdir(exist_ok=True)
    with tarfile.open(p) as t:t.extractall(dest,filter='data')
    return dict(component=component,arch=arch,version=manifest[component]['version'],sha256=sha,size=p.stat().st_size)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,items))
(P/'logs/cuda-u2-component-verification.json').write_text(json.dumps(results,indent=2))
print(json.dumps(dict(release=manifest['release_label'],components=len(results),all_sha_match=True)))
