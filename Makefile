.PHONY: install lint fmt test docker

install:
	pip install -e .

lint:
	ruff .

fmt:
	isort .
	black .

test:
	pytest

docker:
	docker-compose up