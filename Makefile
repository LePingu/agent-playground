# Makefile for Agent Playground development

.PHONY: help install install-dev test test-unit test-integration test-e2e lint format check clean docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package and dependencies"
	@echo "  install-dev  - Install package in development mode with dev dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e     - Run end-to-end tests only"
	@echo "  lint         - Run linting (ruff and mypy)"
	@echo "  format       - Format code with black"
	@echo "  check        - Run all quality checks"
	@echo "  clean        - Clean up build artifacts"
	@echo "  docs         - Build documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

test-cov:
	pytest tests/ --cov=agent_playground --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

check: lint test
	@echo "All checks passed!"

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Development
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make check' to run quality checks"

# Build and release
build:
	python -m build

release: clean build
	python -m twine upload dist/*

# Docker (if using containers)
docker-build:
	docker build -t agent-playground .

docker-run:
	docker run -it --rm agent-playground

# Environment management
env-check:
	agent-playground config --validate

env-info:
	agent-playground info --verbose
