# Safe developer-host checks only. No boot tools, GPU loads or target network access.
.PHONY: check gates asset-plan source-map docs

check:
	python3 tools/verify_manifest.py
	python3 tools/check_repo_release.py

gates:
	python3 tools/check_dual_boot_readiness.py; test $$? -eq 2
	python3 tools/check_program_readiness.py --summary; test $$? -eq 2

asset-plan:
	python3 tools/check_offline_assets.py; test $$? -eq 2

source-map:
	python3 tools/check_source_map.py

docs:
	@echo "Read docs/START_HERE.md and docs/MASTER_IMPLEMENTATION_PLAN.md"
