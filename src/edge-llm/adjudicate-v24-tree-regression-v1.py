"""Current Tree restoration and own-Target recall gates; scope numerical/state/production gaps explicitly."""
import csv,datetime,hashlib,json,pathlib
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');E=P/'evidence';read=lambda n:json.loads((E/n).read_text())
assets=read('V24-tree-assets-v1-admission.json');restored=read('V24-tree-own-target64-v2-result.json');restore_guard=read('V24-tree-own-target64-v2-guard-result.json')
assert assets['status']=='PASS_CURRENT_ORIGINAL_TREE_ASSETS_READONLY_ADMISSION'
Tree64=restored['cases'][0];assert Tree64['strict_oracle']and'END_ID'in Tree64['finish_reason']
assert Tree64['output_ids']==read('S1-runtime-v1-65536-result.json')['cases'][0]['output_ids']and Tree64['Graph_replays']['successes']==44
proofs=[]
for tier,label in [(65536,'64'),(204800,'200')]:
    name=f'V24-tree-target-only{label}-v1';run=read(name+'-result.json');guard=read(name+'-guard-result.json');case=run['cases'][0]
    assert guard['returncode']==0 and not guard['stop_reason']and not guard['GPU_kernel_error_candidates']
    assert case['natural_EOS']and case['strict_oracle']and case['strict_Token_equal_with_Tree']
    ref=Tree64 if tier==65536 else read('S1-runtime-v1-204800-result.json')['cases'][0]
    assert case['output_ids']==ref['output_ids']and run['native_runtime_sha256']==assets['native_runtime_sha256']
    assert case['speculative_counters']['total_proposed_draft_tokens']==case['speculative_counters']['total_accepted_draft_tokens']==0
    proofs.append(dict(tier_tokens=tier,input_tokens=case['input_tokens'],output_tokens=case['output_tokens'],natural_EOS=True,strict_oracle=True,all_Token_IDs_equal=True,
        Target_only=True,Draft_proposed_and_accepted_zero=True,Target_reused_tokens=case['reused'],Target_computed_suffix=case['computed'],
        Tree_reference='Current restoredTree originalRuntime'if tier==65536 else'Saved qualifiedTree200K sameEngine/runtime;not repeated',
        source=name+'-result.json',source_sha256=hashlib.sha256((E/(name+'-result.json')).read_bytes()).hexdigest(),
        guard=guard['status'],peak_GPU_C=guard['peak_mC']['gpu-thermal']/1000,minimum_UMA_GiB=guard['minimum']['MemAvailable_bytes']/1024**3))
cost=read('V24-existing-tree-bottleneck-bounds-v1.json');cold=next(r for r in cost['cases']if r['tier']==204800 and r['mode']=='COLD_CHUNKED_PREFILL')
R4=pathlib.Path('/mnt/d/Thor64G/R4_LLAMA_CPP_AI_HANDOFF_20261012/Thor_R4_llama_cpp_车机改动说明_20261012.md');assert R4.is_file()
record=dict(status='GO_SCOPED_TREE_RESTORATION_AND_64K200K_OWN_TARGET_RECALL_IDS;FULL_QUALITY_AND_FIRST_VERIFY_STATE_PENDING',
    mainline='OriginalNVIDIA_Qwen3.8_27B_NVFP4+EdgeLLM+Tree8/2/16+FP16KV',native_runtime_sha256=assets['native_runtime_sha256'],
    Engine_assets=assets['engines'],Tree64_actual_restoration=dict(output_tokens=42,strict_oracle=True,all_prior_qualified_IDs_equal=True,actual_successful_Graph_replays=44,
        source='V24-tree-own-target64-v2-result.json:firstcase',raw_guard_exit=restore_guard['returncode'],raw_guard_limit='Secondmode reference cache miss caused inputlength error;firstTreecase completed correctly,not GPU failure'),
    own_Target_reference_gates=proofs,
    qualification_scope='Two frozenlongrecall fixtures only. Target-only uses ownTreeBase Engine withspeculation disabled;not independently rebuilt standaloneEngine or completeThinking/code/JSON/continuous-output suite.',
    first_Verify_logits='PENDING_TREE_SPECIFIC_CAPTURE',first_Verify_GDN_state='PENDING_TREE_SPECIFIC_LIVE_COMMIT_CAPTURE',
    existing_baseline_200K=dict(cold_TTFT_s=207.93473365799582,cold_Decode_tok_s=32.31491352354384,warm_TTFT_s=0.43390328501118347,warm_Decode_tok_s=32.4563254740266,source='S1-runtime-v1-204800-result.json;reusedwithoutrepeat'),
    performance_targets=dict(cold_TTFT_s=180,stretch_TTFT_s=160,Decode_tok_s=36),
    measured_new_optimization_gain='NONE;restore and quality-only stage;no formalbenchmark rows added',
    strongest_existing_Prefill_bound=dict(Base_GPU_prefill_s=cold['total_base_prefill_GPU_s'],all_other_TTFT_cost_upper_s=cold['non_Base_prefill_cost_upper_bound_s'],
        required_TTFT_saving_to180=cold['required_TTFT_saving_to180'],interpretation='Eliminating all nonBase cost alone cannot reach180s;must reduce BaseGPU work. Internal Attention/GDN/FFN split remains unmeasured for this exactTree.'),
    current_kernel_hit_audit=dict(SM110_GDN_Prefill='PENDING_ACTUAL_TREE_HIT_TRACE',FMHA_D256='PENDING_ACTUAL_TREE_HIT_TRACE',Paged_Attention='FP16pagedKV configuration admitted;complete dispatch evidence pending',
        CUDA_Graph='44actualsuccessfulTree64Kreplays',PDL='Capabilities known;no Tree-specific complete launchtrace claimed'),
    R4_reuse=dict(source=str(R4).replace('/mnt/d/','D:/'),sha256=hashlib.sha256(R4.read_bytes()).hexdigest(),
        applicable_ideas=['FFN/SwiGLU/RMS fusion with unchangedquantization','GDN producer/consumer dataflow withF32state','Conv and FP16KV vectorizedcopies'],
        historical_speed_not_transferred=True,Native_FA_F32Q_to_FP16_port_not_admitted=True),
    candidate_exclusions=['Do not repeat rejectedCuTeM16 wholeTree substitution','No FP8KV or approximateTargetAttention','No DFlash optimization on this mainline'],
    protocol_repairs=dict(first_probe='BYPASSneverpublishes;fixedUSE_CACHE',cross_mode='ObservedTree-to-Target cachemiss;Targetprime own canonicalprefix instead;no Runtime or Engine rebuild'),
    DFlash2='FROZEN_BACKUP;S5/S6 not used as Tree failure',K7_R4_Golden_changed=False,production_default_changed=False,production_health='UNPROVEN;preexisting userexclusive RAMmaintenance',
    full_model_quality_PASS=False,production_promotion='NO_GO_PENDING_COMPLETE_GATES',
    next_unique_action='One read-only Tree firstVerify/liveGDN-state and actualSM110 FMHA/GDN kernel-dispatch profile;then choose highestROI exactFP16 Prefill candidate before any optimization A/B')
out=E/'V24-tree-regression-v1-adjudication.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();state=read('../RUN_STATE.json');state.update(updated_at_utc=now,current_gate=record['status'],
    active_job=None,active_gpu_candidate_id=None,V24_tree_regression=record,next_action=record['next_unique_action'])
(P/'RUN_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
verdict=read('../CANDIDATE_VERDICT.json');verdict.update(V24_current=record,next_action=record['next_unique_action'],
    V24_GO='SCOPED_RESTORATION_AND_TWO_RECALL_ID_GATES_ONLY',V24_full_quality=False,V24_production_promotion='NO_GO',DFlash2_current_status='FROZEN_BACKUP_NOT_MAINLINE')
(P/'CANDIDATE_VERDICT.json').write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+'\n')
card=P/'RELEASE_CARD.md';text=card.read_text();marker='\n<!-- V2.4 current -->\n'
card.write_text(text.split(marker)[0]+marker+'V2.4 Tree-only restore PASS on originalRuntimebb83eafd and unchangedEngine69fcec11/Draftdbbe26b0,8/2/16,FP16KV. CurrentTree64K42EOS tokens match priorqualifiedIDs;actual44Graphreplays. OwnTarget-only64K42 and200K151EOS tokens exactly match Tree references(twofrozenrecallfixtures only;200K Treebaseline reused). Fullquality and firstVerify/GDN state audit pending. No performance gain claimed;200Kbaseline207.9347sTTFT/32.3149tok/s. ExistingBaseGPU194.1988s;allotherTTFT13.736s ceiling cannot alone save27.9347sneededfor180s. Next:one Tree-specific read-only state/kernel profile before highestROI exactFP16 Prefill candidate. DFlashfrozenbackup;K7/R4Golden/default unchanged.\n')
index=P/'EVIDENCE_INDEX.tsv';text=index.read_text()
names=['V24-tree-assets-v1-admission.json','V24-tree-own-target64-v1-result.json','V24-tree-own-target64-v1-guard-result.json','V24-tree-own-target64-v2-result.json','V24-tree-own-target64-v2-guard-result.json',
    'V24-tree-target-only64-v1-result.json','V24-tree-target-only64-v1-guard-result.json','V24-tree-target-only200-v1-result.json','V24-tree-target-only200-v1-guard-result.json','V24-existing-tree-bottleneck-bounds-v1.json','V24-tree-regression-v1-adjudication.json']
for name in names:
    if not any(line.split('\t')[0]==name for line in text.splitlines()):
        file=E/name;text+='\t'.join([name,'V24','.json',now,'Tree-only restore and ownTarget recall regression',state['checkpoint_revision'],state['source_commit'],str(file).replace('/mnt/d/','D:/'),hashlib.sha256(file.read_bytes()).hexdigest(),'OriginalRuntime reused;twoTokenIDgates scoped;firststate/kernelcapturepending','GO scopedfixtures;fullquality/productionNO_GO;Golden retained'])+'\n'
index.write_text(text)
with(P/'BENCHMARK_RESULTS.csv').open(newline='')as file:assert len(list(csv.DictReader(file)))==26
print(json.dumps(dict(status=record['status'],own_Target=[dict(tier=r['tier_tokens'],tokens=r['output_tokens'],strict_IDs=r['all_Token_IDs_equal'])for r in proofs],new_performance_gain=False,next_action=record['next_unique_action'])))
