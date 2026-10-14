"""Offline adjudication of complete diagnostic trace, including per-request split enqueues."""
import collections, datetime, hashlib, json, pathlib
P = pathlib.Path(__file__).resolve().parents[1]
E = P / 'evidence'
read = lambda name: json.loads((E / name).read_text())
run = read('V24-tree-layer-profiler-v2-204800-result.json')
guard = read('V24-tree-layer-profiler-v2-204800-guard-result.json')
assert run['status'] == 'FAIL_TREE_PUBLIC_LAYER_PROFILE' and run['error'] == 'AssertionError()'
assert len(run['rows']) == 24 and run['rows'][-1]['label'] == 'COLD_200K_FINAL'
assert guard['returncode'] == 1 and guard['stop_reason'] is None
assert not guard['GPU_kernel_error_candidates'] and max(guard['peak_mC'].values()) < 95000
assert 'assert len(base_records) == len(result[\'rows\'])' in (E / 'V24-tree-layer-profiler-v2-204800.log').read_text()
trace = E / 'V24-tree-layer-profiler-v2-204800-layers.jsonl'
records = [json.loads(line) for line in trace.read_text().splitlines()]
assert len(records) == 96
assert all(r['enqueue_succeeded'] and r['callback_errors'] == 0 for r in records)
base = [r for r in records if r['engine'].endswith('/spec_base.engine')]
draft = [r for r in records if r['engine'].endswith('/spec_draft.engine')]
assert len(base) == len(draft) == 48
assert [r['invocation'] for r in base] == [r['invocation'] for r in draft] == list(range(1,49))
assert all(len(r['layers']) == 1547 for r in base)
assert all(len(r['layers']) == 29 for r in draft)
assert all(r['phase'] in [1,2] for r in records)
reference = read('S1-runtime-v1-204800-result.json')
groups = collections.defaultdict(float)
stages = []
attention_by_layer = collections.defaultdict(float)
for i, row in enumerate(run['rows']):
    b = base[2*i:2*i+2]
    d = draft[2*i:2*i+2]
    expected_ids = (reference['primer_records'][i]['discarded_primer_output_ids'] if i < 23
                    else reference['cases'][0]['output_ids'][:1])
    assert row['output_ids'] == expected_ids
    assert sum(r['physical_tokens'] for r in b) == row['computed']
    expected_shapes = [8192,15] if i < 23 else [7168,102]
    assert [r['physical_tokens'] for r in b] == expected_shapes
    assert [r['physical_tokens'] for r in d] == ([8192,15] if i == 0 else [8193,15] if i < 23 else [7169,102])
    buckets = collections.defaultdict(float)
    for rec in b:
        for layer in rec['layers']:
            name = layer['name']
            kind = ('Attention_named_regions' if name.startswith('attention_') else
                    'Matrix_Multiply_named_regions' if '[Matrix Multiply]' in name else
                    'Unnamed_plugins_semantics_unproven' if '[PluginV3_V3ONE]' in name else
                    'Fused_FC_named_regions' if name.startswith('__myl_Fc') else 'Other_fused_regions')
            buckets[kind] += layer['ms']
            if name.startswith('attention_'): attention_by_layer[name] += layer['ms']
    for k,v in buckets.items(): groups[k] += v
    stages.append(dict(label=row['label'], input_tokens=row['input_tokens'], computed=row['computed'],
        reused=row['reused'], physical_base_tokens=[r['physical_tokens'] for r in b],
        base_layer_sum_ms=sum(r['layer_time_sum_ms'] for r in b),
        base_enqueue_wall_ms=sum(r['enqueue_wall_ms'] for r in b),
        draft_layer_sum_ms=sum(r['layer_time_sum_ms'] for r in d),
        groups_ms=dict(buckets), saved_token_match=True))
base_sum = sum(r['layer_time_sum_ms'] for r in base)
draft_sum = sum(r['layer_time_sum_ms'] for r in draft)
assert abs(sum(groups.values())-base_sum) < .01
assert len(attention_by_layer) == 16
result = dict(status='PASS_OFFLINE_COMPLETE_200K_TREE_PUBLIC_LAYER_ATTRIBUTION_AND_SAVED_TOKENS_ONLY',
    timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    harness_terminal_status_preserved=run['status'], harness_exit_code=guard['returncode'],
    terminal_assertion_cause='Expected one Base enqueue per request;actual cache-aligned split uses two. All24requests and96enqueues completed before assertion.',
    new_GPU_run_required=False, trace_SHA=hashlib.sha256(trace.read_bytes()).hexdigest(),
    diagnostic_runtime_SHA=run['diagnostic_runtime_sha256'], original_plugin_SHA='8fb2fb35b60b097c3a3f30c54fdb45d65c30469147c49ac61bb76468fa650c63',
    Graph=False, Tree='8/2/16', KV='FP16', actual_input_tokens=195686,
    canonical_primer_token_checks_passed=23, final_first_token=[90], full_quality_repeated=False,
    base_enqueues=48, draft_enqueues=48, complete_base_layer_rows=48*1547,
    base_diagnostic_layer_sum_s=base_sum/1000, draft_diagnostic_layer_sum_s=draft_sum/1000,
    Base_groups_s={k:v/1000 for k,v in groups.items()},
    Attention_fraction_of_Base_diagnostic_layer_sum=groups['Attention_named_regions']/base_sum,
    attention_layers_total_s={k:v/1000 for k,v in attention_by_layer.items()},
    stage_records=stages, GPU_peak_C=guard['peak_mC']['gpu-thermal']/1000,
    min_UMA_GiB=guard['minimum']['MemAvailable_bytes']/1024**3, GPU_errors=[],
    native200K_TTFT_baseline_s=207.934733658, target_TTFT_s=180,
    required_net_saving_s=207.934733658-180,
    new_native_performance_gain='NONE;diagnostic profiling is not an uninstrumented performance A/B',
    actual_kernel_dispatch_proven=False,
    selected_region='FP16 D256 Attention long-cache path',
    selection_rationale='Direct full200K Tree trace, rather than extrapolating previous DFlash or short-query growth.',
    limitations=['IProfiler intervals can overlap or include instrumentation overhead;not exclusive kernel cost or a promised speedup.',
                 'Unnamed plugins not relabeled as GDN without a verified semantic map.',
                 'Original plugin already contains SM110 D256 native-paged variants;presence is not proof of which variant executed.',
                 'Current source differs from original plugin provenance;do not replace entire plugin on an assumed equivalence.'],
    next_action='Resolve original FP16 Attention dispatch/tile configuration before compiling one narrowly scoped SM110 D256 candidate;retain exact same weights,FP16 KV and original Engine.',
    Golden_changed=False, production_admission='NO_GO', generic_CUDA13x_PASS=False)
path=E/'V24-tree-layer-profiler-v2-200K-offline-adjudication.json'
path.write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['status','base_diagnostic_layer_sum_s','draft_diagnostic_layer_sum_s','Base_groups_s','Attention_fraction_of_Base_diagnostic_layer_sum','GPU_peak_C','min_UMA_GiB','next_action']}))
