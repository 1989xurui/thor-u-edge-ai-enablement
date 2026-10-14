"""One bounded matched Graph comparison; never repeats completed receipts."""
import json,os,pathlib,shutil,subprocess,time
root=pathlib.Path('/zeekr_data/nvidia-native-ai-v2')
assert json.loads((root/'native-mtp-paired8k-result.json').read_text())['status']=='PASS_NATIVE_27B_EDGE_MTP_PAIRED8K_QUALITY_ONLY'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='9d74daba-0347-489c-9192-2d117806cbe7'
(root/'tmp/native-tree-bypass8k-launch-once').mkdir()
from cuda.bindings import runtime as cuda
def sample():
    memory={l.split(':')[0]:int(l.split()[1])for l in pathlib.Path('/proc/meminfo').read_text().splitlines()}
    status,free,total=cuda.cudaMemGetInfo();assert int(status)==0
    return dict(uptime_s=float(pathlib.Path('/proc/uptime').read_text().split()[0]),MemAvailable_KiB=memory['MemAvailable'],GPU_free_bytes=free,
                persistent_free_bytes=min(shutil.disk_usage(root).free,shutil.disk_usage('/zeekr_map').free),Tj_mC=int(pathlib.Path('/sys/class/thermal/thermal_zone0/temp').read_text()))
log=root/'logs/native-tree-bypass8k.log';result_path=root/'native-tree-bypass8k-guard-result.json'
assert not result_path.exists(),'No automatic paired run repeat'
before=sample();minimum=dict(before);max_tj=before['Tj_mC'];max_rss=0;failure=None;start=time.monotonic()
assert before['MemAvailable_KiB']>=5*1024**2 and before['GPU_free_bytes']>=2*1024**3 and before['persistent_free_bytes']>=12*1024**3 and before['Tj_mC']<95000,before
with log.open('w')as output,(root/'logs/native-tree-bypass8k-telemetry.jsonl').open('w')as telemetry:
    process=subprocess.Popen(['sh','/v2/python-native-tree-bypass8k.sh','/v2/run-native-tree-bypass8k.py'],stdout=output,stderr=subprocess.STDOUT)
    result=dict(status='RUNNING',pid=process.pid,before=before,boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip())
    result_path.write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
    while process.poll()is None:
        sample_now=sample();max_tj=max(max_tj,sample_now['Tj_mC'])
        for key in ('MemAvailable_KiB','GPU_free_bytes','persistent_free_bytes'):minimum[key]=min(minimum[key],sample_now[key])
        try:max_rss=max(max_rss,next(int(l.split()[1])for l in pathlib.Path(f'/proc/{process.pid}/status').read_text().splitlines()if l.startswith('VmHWM:')))
        except (FileNotFoundError,StopIteration):pass
        telemetry.write(json.dumps(sample_now)+'\n');telemetry.flush()
        if sample_now['MemAvailable_KiB']<5*1024**2:failure='MemAvailable <5GiB'
        elif sample_now['GPU_free_bytes']<2*1024**3:failure='GPU free <2GiB'
        elif sample_now['persistent_free_bytes']<12*1024**3:failure='Persistent free <12GiB'
        elif max_tj>=95000:failure='Tj >=95C'
        elif time.monotonic()-start>300:failure='Native generation job exceeded 300s bound'
        if failure:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            break
        time.sleep(1)
    returncode=process.wait()
result.update(status='PASS_PROCESS_EXIT_ONLY'if returncode==0 else'FAIL_NATIVE_GENERATION',returncode=returncode,failure=failure,
              elapsed_s=time.monotonic()-start,minimum=minimum,maximum_Tj_mC=max_tj,observed_peak_RSS_KiB=max_rss,after=sample())
result_path.write_text(json.dumps(result,indent=2));os.sync();print(json.dumps(result),flush=True)
