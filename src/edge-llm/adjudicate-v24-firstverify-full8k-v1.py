import csv,datetime,hashlib,json,pathlib
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');E=P/'evidence'
def read(name):return json.loads((E/name).read_text())
capture=read('V24-tree-firstverify-v5-result.json');analysis=read('V24-tree-firstverify-v5-analysis.json')
full=read('V24-tree-full8k-v1-result.json');guard=read('V24-tree-full8k-v1-guard-result.json')
backup=read('V24-tree-native-valid-v1-host-receipt.json');terminal=read('V24-tree-close-v1-terminal.json')
observer=read('V24-launch-forwarding-cpu-repro-v1.json')
assert full['status']=='PASS_FULL8K_OWN_TARGET_IDS_AND_ORACLE'and full['strict_all_IDs_equal']
assert guard['returncode']==0 and not guard['stop_reason']and not guard['GPU_kernel_error_candidates']
assert terminal['status']=='PASS_CPU_ONLY_TREE_FULL8K_TERMINAL_PROTECTION'and not terminal['GPU_FD_owners']
assert analysis['all_finite'] and analysis['GDN_state_tensor_count_per_stage']==analysis['conv_state_tensor_count_per_stage']==48
assert backup['status']=='PASS_HOST_SHA_ALL_BLOBS_AND_LOSSLESS_ALL_VALID_KV_RECONSTRUCTION'
assert observer['status']=='NO_GO_V2_OBSERVER_FORWARDING'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();gate='GO_SCOPED_TREE_8K64K200K_RECALL_IDS;FIRST_VERIFY_FLOAT_DIFFERENCES_RECORDED;FULL_QUALITY_AND_PRODUCTION_NO_GO'
next_action='One safe nativeTree Prefill layer/kernel-dispatch profile on originalRuntime,after CPU forwarding-contract validation;choose highestROI exactFP16 Prefill candidate;no repeated full8K64K200K quality or speed runs'
evidence=dict(status=gate,timestamp_utc=now,previous_goal_turn_classification='NO_PROGRESS_STATUS_ONLY',this_goal_turn_classification='PROGRESS_REAL_FIRST_VERIFY_ALL_STATE_CAPTURE_AND_FULL8K_OWN_TARGET_IDS',
    Runtime_SHA=capture['runtime_sha256'],Runtime_recompiled=False,Engine_recompiled=False,weights_or_quantization_changed=False,
    first_Verify=dict(input_tokens=8207,context_length=analysis['first_committed_Tree_context_length'],matched_Target_AR_step=analysis['matched_first_Verify_Target_round'],
        prefill_all_states_and_logits_bitwise_equal=True,GDN_layers=48,conv_layers=48,FP16_attention_KV_layers=16,all_finite=True,
        committed_states_captured_before_cleanup=True,all_KV_prefixes_bitwise_unchanged=True,
        first_Verify_logits=analysis['logits'][1],GDN_max_relative_RMS=max(r['relative_RMS']for r in analysis['tensors']if r['stage']=='first-verify'and r['tensor'].endswith('recurrent_state')),
        layer0_recurrent=next(r for r in analysis['tensors']if r['stage']=='first-verify'and r['tensor']=='layer_0.recurrent_state'),
        layer0_conv_bitwise_equal=True,first9_IDs_equal=True,numerical_tolerance_PASS='NOT_CLAIMED',
        interpretation='Committed states and logits differ numerically afterVerify;no Token difference in observed fixtures. Not proof of state corruption or wholemodel numerical equivalence.',
        short_capture_spec_counters='UNAVAILABLE_PROFILE_DISABLED;do not interpret zero counters as absence of Tree'),
    full8K=dict(input_tokens=8207,Tree_output_tokens=full['cases'][0]['output_tokens'],Target_output_tokens=full['cases'][1]['output_tokens'],
        all368_Token_IDs_equal=True,both_natural_EOS=True,both_strict_JSON_oracle=True,
        Tree_Graph=full['cases'][0]['Graph_replays'],Target_Graph=full['cases'][1]['Graph_replays'],
        Tree_spec_metrics=full['cases'][0]['speculative_counters'],Target_spec_metrics=full['cases'][1]['speculative_counters'],
        GPU_peak_C=guard['peak_mC']['gpu-thermal']/1000,minimum_UMA_GiB=guard['minimum']['MemAvailable_bytes']/1024**3,
        source='V24-tree-full8k-v1-result.json',new_performance_gain='NONE;quality gate only'),
    kernel_audit=dict(new_v2_launch_observer='NO_GO_CPU_SELF_FORWARDING_REPRO;removed;originalRuntime subsequently completed',
        actual_SM110_FMHA_D256_and_GDN_prefill_dispatch='PENDING_SAFE_NATIVE_TREE_PROFILE',complete_GPU_time_split='PENDING'),
    backup=backup,terminal=terminal,full_model_quality_PASS=False,
    remaining_quality='Three recall fixtures only;Thinking/code/generalJSON/continuous-output/independent standaloneEngine not fully qualified',
    production_promotion='NO_GO',K7_R4_Golden_changed=False,production_default_changed=False,DFlash2='FROZEN_BACKUP',
    new_performance_gain='NONE',next_unique_action=next_action)
out=E/'V24-tree-firstverify-full8k-v1-adjudication.json';out.write_text(json.dumps(evidence,indent=2))
benchmark=P/'BENCHMARK_RESULTS.csv';before=hashlib.sha256(benchmark.read_bytes()).hexdigest()
for filename in ['RUN_STATE.json','CANDIDATE_VERDICT.json']:
    path=P/filename;state=json.loads(path.read_text());state.update(updated_at_utc=now,current_gate=gate,next_action=next_action,
        active_gpu_candidate_id=None,active_job=None,previous_goal_turn='PROGRESS_ORIGINAL_TREE_FIRST_VERIFY_AND_FULL8K_OWN_TARGET',
        V24_tree_firstVerify=evidence,V24_terminal_state=terminal)
    if filename=='CANDIDATE_VERDICT.json':
        current=state.setdefault('V24_current',{});current.update(status=gate,first_Verify_logits=evidence['first_Verify'],
            first_Verify_GDN_state='CAPTURED_ALL48_REAL_COMMITTED_STATES;FLOAT_DIFFERENCES_RECORDED',
            full8K_own_Target_gate=evidence['full8K'],full_model_quality_PASS=False,production_promotion='NO_GO',next_unique_action=next_action,
            current_kernel_hit_audit=evidence['kernel_audit'],qualification_scope=evidence['remaining_quality'])
        state['V24_GO']='SCOPED_8K64K200K_RECALL_IDS_ONLY';state['V24_full_quality']=False
    else:
        session=state.setdefault('tree_session',{});session.update(status='ORIGINAL_TREE_SCOPED_QUALITY_GO_NO_ACTIVE_GPU_JOB',pid=None,current_gate=gate)
        state.setdefault('V24_tree_regression',{}).update(first_Verify_capture=evidence['first_Verify'],full8K_own_Target=evidence['full8K'],next_unique_action=next_action)
    path.write_text(json.dumps(state,indent=2))
card=P/'RELEASE_CARD.md'
with card.open('a')as f:f.write('\n\nV2.4 '+now+': originalTree full8K/64K/200K recall ID gates are scoped GO. Full8K:8207 input,368 naturalEOS output,ownTarget exactIDs andJSON oracle. FirstVerify all48GDN/48Conv states andFP16KV captured;float differences measured,not numerical-equivalence PASS. Newlaunchobserverv2 is NO_GO andremoved. Fullquality/production remain NO_GO. No newperformance gain. Next:'+next_action+'\n')
items=[('V24_FIRST_VERIFY_NATIVE','V24-tree-firstverify-v5-analysis.json','analyze-v24-tree-firstverify-v5.py'),
    ('V24_FULL8K_OWN_TARGET','V24-tree-full8k-v1-result.json','run-v24-tree-full8k-v1.py'),
    ('V24_LAUNCH_OBSERVER_CPU_NO_GO','V24-launch-forwarding-cpu-repro-v1.json','reproduce-v24-launch-forwarding-cpu.py'),
    ('V24_VALID_TENSOR_BACKUP','V24-tree-native-valid-v1.tar.gz','compact-v24-tree-native-valid-v1.py'),
    ('V24_VALID_TENSOR_HOST_SHA','V24-tree-native-valid-v1-host-receipt.json','download-verify-v24-native-valid-v1.py'),
    ('V24_FIRST_VERIFY_FULL8K_VERDICT',out.name,'adjudicate-v24-firstverify-full8k-v1.py')]
index=P/'EVIDENCE_INDEX.tsv';existing={line.split('\t')[0]for line in index.read_text().splitlines()}
with index.open('a',newline='')as f:
    writer=csv.writer(f,delimiter='\t')
    for item,name,producer in items:
        if item in existing:continue
        artifact=E/name;sha=backup['archive_sha256']if name.endswith('.tar.gz')else hashlib.sha256(artifact.read_bytes()).hexdigest()
        source_sha=hashlib.sha256((P/'scripts'/producer).read_bytes()).hexdigest()
        writer.writerow([item,'V2.4','actual_evidence',now,'originalShared200KTree','7d0fd155118901373eb0fd13ed3aae68f95be747bc205be72ebc41739c25ee80',source_sha,
            'D:\\Thor64G\\THOR_NVIDIA_NVFP4_20261013\\evidence\\'+name,sha,'originalRuntimebb83;weightsunchanged','Scopedquality;fullquality/production notPASS'])
assert hashlib.sha256(benchmark.read_bytes()).hexdigest()==before
print(json.dumps(dict(status=gate,full8K_IDs=True,first_Verify_all_states_captured=True,benchmark_unchanged=True,next_action=next_action)))
