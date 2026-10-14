import pathlib, struct, json, hashlib
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
p=P/'artifacts/g35/nvgpu.ko'; b=p.read_bytes()
h=struct.unpack_from('<16sHHIQQQIHHHHHH',b)
sections=[struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*h[11]) for i in range(h[12])]
sn=sections[h[13]]; names=b[sn[4]:sn[4]+sn[5]]
def z(s,o):return s[o:s.index(b'\0',o)].decode()
out=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),aarch64=h[2]==183,table_entries=[])
for s in sections:
    if z(names,s[0])!='.symtab':continue
    st=sections[s[6]]; strings=b[st[4]:st[4]+st[5]]
    for off in range(s[4],s[4]+s[5],s[9]):
        n,info,other,idx,value,size=struct.unpack_from('<IBBHQQ',b,off)
        if z(strings,n)!='__mod_pci__nvgpu_pci_table_device_table':continue
        sec=sections[idx]; raw=b[sec[4]+value:sec[4]+value+size]
        assert size%40==0
        for i in range(0,size,40):
            vendor,device,subvendor,subdevice,cls,mask,driver_data,override=struct.unpack_from('<6IQI',raw,i)
            if vendor==0x10de and device==0x2b00:
                out['table_entries'].append(dict(vendor=hex(vendor),device=hex(device),subvendor=hex(subvendor),subdevice=hex(subdevice),pci_class=hex(cls),class_mask=hex(mask),driver_data=driver_data,override_only=override))
assert out['aarch64'] and any(e['driver_data']==5 for e in out['table_entries'])
(P/'logs/compiled-pci-verification.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
