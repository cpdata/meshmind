.PHONY: install lint fmt fmt-check typecheck test check docker clean

install:
	pip install -e .

lint:
	ruff check .

fmt:
	ruff format .

fmt-check:
	ruff format --check .
	ruff check .
	toml-sort --check pyproject.toml
	yamllint .github/workflows

typecheck:
	pyright
	python -m typeguard --check meshmind

test:
	pytest

check: fmt-check lint typecheck test

clean:
	rm -rf .pytest_cache .ruff_cache

docker:
	docker compose up
