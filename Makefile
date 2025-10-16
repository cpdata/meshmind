.PHONY: install lint fmt fmt-check typecheck test check docker clean docs-guard benchmarks protos protos-check

BENCH_DIR := build/benchmarks

install:
	python -m pip install -e .[dev,docs,testing]

lint:
	ruff check .

fmt:
	ruff format .

fmt-check:
        ruff format --check .
        ruff check .
        toml-sort --check pyproject.toml
        yamllint .github/workflows

docs-guard:
        python scripts/check_docs_sync.py --base $${BASE_REF:-origin/main}

protos:
        python scripts/generate_protos.py

protos-check:
        python scripts/check_protos.py

typecheck:
	pyright
	python -m typeguard --check meshmind

test:
        pytest

benchmarks:
        mkdir -p $(BENCH_DIR)
        python scripts/evaluate_importance.py --synthetic-count 48 --namespace benchmarks --output $(BENCH_DIR)/importance.json
        python scripts/consolidation_benchmark.py --namespaces 2 --groups 6 --duplicates 3 --iterations 2 --output $(BENCH_DIR)/consolidation.json
        python scripts/benchmark_pagination.py --backend memory --count 500 --page-size 100 --iterations 2 --output $(BENCH_DIR)/pagination.json

check: fmt-check lint typecheck test docs-guard protos-check

clean:
	rm -rf .pytest_cache .ruff_cache

docker:
	docker compose up
