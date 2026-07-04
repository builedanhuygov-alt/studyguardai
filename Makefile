.PHONY: install test cov lint format typecheck bench run docker-build clean

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

cov:
	pytest --cov=studyguard --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	black .
	ruff check --fix .

typecheck:
	mypy studyguard

bench:
	python benchmarks/benchmark_pipeline.py

run:
	python -m studyguard

docker-build:
	docker build -t studyguard-ai .

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info
