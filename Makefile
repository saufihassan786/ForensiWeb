# ==============================================================================
# ForensiWeb — Development Makefile
# ==============================================================================
# Standard command interface for Linux, macOS, WSL, and CI environments.
# On Windows, python scripts/development/dev.py provides an equivalent CLI.
# ==============================================================================

.PHONY: help setup validate-env test test-unit test-integration test-hygiene clean lab-up lab-down lab-reset

PYTHON ?= python

help:
	@echo "ForensiWeb Development Commands:"
	@echo "  make setup            Initialize local environment (.env) and validate configuration"
	@echo "  make validate-env     Validate active .env or .env.example against schema"
	@echo "  make test             Execute complete automated test suite"
	@echo "  make test-unit        Execute unit test suite"
	@echo "  make test-integration Execute integration test suite"
	@echo "  make test-hygiene     Verify git ignore rules and repository hygiene"
	@echo "  make clean            Clean up runtime caches, pycache, and temporary files"
	@echo "  make lab-up           Start isolated Docker laboratory containers"
	@echo "  make lab-down         Stop and remove Docker laboratory containers"
	@echo "  make lab-reset        Reset laboratory state and clean working evidence"

setup:
	$(PYTHON) scripts/setup/init_env.py
	$(PYTHON) scripts/setup/validate_env.py

validate-env:
	$(PYTHON) scripts/setup/validate_env.py

test:
	$(PYTHON) -m pytest

test-unit:
	$(PYTHON) -m pytest -m "unit"

test-integration:
	$(PYTHON) -m pytest -m "integration"

test-hygiene:
	$(PYTHON) scripts/testing/check_git_hygiene.py

clean:
	$(PYTHON) scripts/development/dev.py clean

lab-up:
	docker compose up -d

lab-down:
	docker compose down

lab-reset:
	$(PYTHON) scripts/development/dev.py lab-reset
