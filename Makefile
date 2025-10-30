.PHONY: help install install-dev test test-unit test-integration coverage lint format clean run setup pre-commit security

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make setup            - Complete project setup (install + pre-commit)"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage         - Generate coverage report"
	@echo "  make lint             - Run all linting checks"
	@echo "  make format           - Format code with black and isort"
	@echo "  make security         - Run security scans"
	@echo "  make pre-commit       - Install pre-commit hooks"
	@echo "  make run              - Run the application"
	@echo "  make clean            - Clean up generated files"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup: install-dev pre-commit
	@echo "✓ Project setup complete!"

# Pre-commit hooks
pre-commit:
	pip install pre-commit
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

# Testing
test:
	pytest -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest --cov=src --cov=api --cov-report=html --cov-report=term-missing
	@echo "✓ Coverage report generated in htmlcov/"

# Code quality
lint:
	@echo "Running Black check..."
	black --check api/ src/ tests/ config/
	@echo "Running isort check..."
	isort --check-only --profile black api/ src/ tests/ config/
	@echo "Running flake8..."
	flake8 api/ src/ config/ --max-line-length=120 --extend-ignore=E203,W503
	@echo "Running pylint..."
	pylint api/ src/ config/ --max-line-length=120 --fail-under=7.0
	@echo "✓ All linting checks passed"

format:
	@echo "Formatting code with Black..."
	black api/ src/ tests/ config/
	@echo "Sorting imports with isort..."
	isort --profile black api/ src/ tests/ config/
	@echo "✓ Code formatted successfully"

# Security
security:
	@echo "Running Bandit security scan..."
	bandit -r api/ src/ config/ -ll
	@echo "Checking for known vulnerabilities..."
	safety check || true
	@echo "✓ Security scan complete"

# Run application
run:
	python start_api.py

# Cleanup
clean:
	@echo "Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -f coverage.xml
	rm -f bandit-report.json
	@echo "✓ Cleanup complete"

# Docker support (if needed)
docker-build:
	docker build -t finance-assets-api .

docker-run:
	docker run -p 8000:8000 --env-file .env finance-assets-api

# Database
db-setup:
	@echo "Starting MongoDB with Docker..."
	docker run -d -p 27017:27017 --name finance-assets-mongo mongo:7.0
	@echo "✓ MongoDB container started"

db-stop:
	docker stop finance-assets-mongo
	docker rm finance-assets-mongo
	@echo "✓ MongoDB container stopped and removed"
