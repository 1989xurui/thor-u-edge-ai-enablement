"""Read-only thermal/power/clock inventory. No fan, clock, thermal or driver writes."""
import glob,json,pathlib,time
P=pathlib.Path;root=P('/zeekr_data/nvidia-native-ai-v2')
def read(p):
    try:return P(p).read_text().strip()[:12000]
    except (OSError,UnicodeError)as error:return 'UNAVAILABLE:'+str(error)[:160]
def fields(directory,names):return {name:read(directory/name)for name in names if(directory/name).exists()}
result=dict(boot_id=read('/proc/sys/kernel/random/boot_id'),uptime=read('/proc/uptime'),thermal_zones=[],cooling_devices=[],hwmon=[],devfreq=[],cpufreq=[],pwm=[],bpmp_clocks=[])
for name in sorted(glob.glob('/sys/class/thermal/thermal_zone*')):
    p=P(name);record=dict(path=name,**fields(p,['type','temp','mode','policy','sustainable_power','offset','slope']))
    record['trips']={v.name:read(v)for v in p.glob('trip_point_*')};record['bindings']={v.name:str(v.resolve())for v in p.glob('cdev*')if v.is_symlink()};result['thermal_zones'].append(record)
for name in sorted(glob.glob('/sys/class/thermal/cooling_device*')):
    p=P(name);result['cooling_devices'].append(dict(path=name,**fields(p,['type','cur_state','max_state'])))
for name in sorted(glob.glob('/sys/class/hwmon/hwmon*')):
    p=P(name);record=dict(path=name,real_path=str(p.resolve()),name=read(p/'name'),sensors={})
    for pattern in('temp*','power*','in*_input','in*_label','curr*_input','curr*_label','fan*','pwm*'):
        record['sensors'].update({v.name:read(v)for v in p.glob(pattern)if v.is_file()})
    result['hwmon'].append(record)
for name in sorted(glob.glob('/sys/class/devfreq/*')):
    p=P(name);result['devfreq'].append(dict(path=name,real_path=str(p.resolve()),**fields(p,['name','cur_freq','governor','min_freq','max_freq','available_frequencies','trans_stat','load'])))
for name in sorted(glob.glob('/sys/devices/system/cpu/cpufreq/policy*')):
    p=P(name);result['cpufreq'].append(dict(path=name,**fields(p,['scaling_driver','scaling_governor','scaling_cur_freq','scaling_min_freq','scaling_max_freq','cpuinfo_max_freq'])))
for name in sorted(glob.glob('/sys/class/pwm/pwmchip*')):
    p=P(name);result['pwm'].append(dict(path=name,real_path=str(p.resolve()),npwm=read(p/'npwm'),channels=[dict(path=str(v),**fields(v,['period','duty_cycle','enable','polarity']))for v in p.glob('pwm[0-9]*')]))
clocks=P('/sys/kernel/debug/bpmp/debug/clk');result['bpmp_clock_names']=[p.name for p in clocks.glob('*')]if clocks.exists()else[]
for p in clocks.glob('*'):
    if any(x in p.name.lower()for x in('gpc','gpu','emc','fan')):result['bpmp_clocks'].append(dict(path=str(p),**fields(p,['rate','min_rate','max_rate','state','clk_tree'])))
result['modules']=[line for line in read('/proc/modules').splitlines()if any(x in line.lower()for x in('thermal','bpmp','nvgpu','fan','pwm','devfreq','actmon'))]
result['original_fan_paths']=[str(p)for pattern in('/new_root/etc/*fan*','/new_root/etc/systemd/system/*fan*','/new_root/usr/sbin/*fan*','/new_root/usr/bin/*tegrastats*')for p in map(P,glob.glob(pattern))]
result['thermal_samples']=[]
for i in range(5):
    result['thermal_samples'].append(dict(uptime=read('/proc/uptime'),values={p.name:read(p/'temp')for p in map(P,glob.glob('/sys/class/thermal/thermal_zone*'))}));time.sleep(1)
(root/'thermal-performance-readonly.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
