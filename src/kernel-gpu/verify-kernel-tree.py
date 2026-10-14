import tarfile, hashlib, json, pathlib
root = pathlib.Path(r'D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013')
archive = root / 'inputs/source-archives/Linux_for_Tegra/source/kernel_src.tbz2'
prefix = 'kernel/kernel-noble/'
trees = {'': {}}
file_oids = {}
count = 0
def ensure(d):
    if d not in trees:
        trees[d] = {}
        parent, _, name = d.rpartition('/')
        ensure(parent)
        trees[parent][name] = ('40000', d)
with tarfile.open(archive, 'r|bz2') as tf:
    for member in tf:
        if not member.name.startswith(prefix):
            continue
        rel = member.name[len(prefix):].rstrip('/')
        if not rel or member.isdir():
            continue
        parent, _, name = rel.rpartition('/')
        ensure(parent)
        if member.isfile():
            h = hashlib.sha1(f'blob {member.size}\0'.encode())
            f = tf.extractfile(member)
            while chunk := f.read(1024*1024):
                h.update(chunk)
            mode = '100755' if member.mode & 0o111 else '100644'
        elif member.issym():
            target = member.linkname.encode()
            h = hashlib.sha1(f'blob {len(target)}\0'.encode() + target)
            mode = '120000'
        else:
            raise RuntimeError(f'Unsupported tar member: {rel}')
        trees[parent][name] = (mode, h.digest())
        file_oids[rel] = dict(mode=mode, oid=h.hexdigest())
        count += 1
def tree_hash(d):
    entries = trees[d]
    payload = b''
    for name in sorted(entries, key=lambda n: (n + ('/' if entries[n][0] == '40000' else '')).encode()):
        mode, value = entries[name]
        oid = tree_hash(value) if mode == '40000' else value
        payload += mode.encode() + b' ' + name.encode() + b'\0' + oid
    return hashlib.sha1(f'tree {len(payload)}\0'.encode() + payload).digest()
actual = tree_hash('').hex()
result = dict(commit='78272943bba3a47e633b28963b0cda60de503500', expected_tree='4bc6b7d68853f74a6c7466b46f98f70df6821738', actual_tree=actual, files=count, match=actual == '4bc6b7d68853f74a6c7466b46f98f70df6821738')
expected_file = root / 'inputs/kernel-expected-tree.tsv'
if expected_file.exists():
    expected = {}
    for line in expected_file.read_text().splitlines():
        metadata, name = line.split('\t', 1)
        mode, kind, oid = metadata.split()
        expected[name] = dict(mode=mode, oid=oid)
    differences = [dict(path=n, expected=expected.get(n), archive=file_oids.get(n)) for n in sorted(set(expected)|set(file_oids)) if expected.get(n) != file_oids.get(n)]
    result['expected_files'] = len(expected)
    result['differences'] = differences
(root / 'inputs/kernel-tree-verification.json').write_text(json.dumps(result, indent=2))
print(json.dumps({k:v for k,v in result.items() if k != 'differences'}))
if 'differences' in result:
    print('differences=', len(result['differences']))
    print(json.dumps(result['differences'][:12]))
