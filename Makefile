.PHONY: install lint fmt fmt-check typecheck test check docker clean docs-guard

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

typecheck:
	pyright
	python -m typeguard --check meshmind

test:
	pytest

check: fmt-check lint typecheck test docs-guard

clean:
	rm -rf .pytest_cache .ruff_cache

docker:
	docker compose up
