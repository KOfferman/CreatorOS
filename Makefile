.PHONY: dev test seed migrate api-test web-test install

API_DIR := api
WEB_DIR := web
API_VENV := $(API_DIR)/.venv
API_PYTHON := $(API_VENV)/bin/python
API_PIP := $(API_VENV)/bin/pip

dev:
	$(MAKE) -C $(API_DIR) dev

install:
	python3 -m venv $(API_VENV)
	$(API_PIP) install --upgrade pip
	$(API_PIP) install -r $(API_DIR)/requirements.txt
	cd $(WEB_DIR) && corepack pnpm install --frozen-lockfile
	@test -f $(WEB_DIR)/.env.local || cp $(WEB_DIR)/.env.example $(WEB_DIR)/.env.local
	@test -f $(API_DIR)/.env.local || cp $(API_DIR)/.env.example $(API_DIR)/.env.local

test: api-test web-test

api-test: install
	cd $(API_DIR) && ../$(API_VENV)/bin/python -m pytest tests -q

web-test: install
	cd $(WEB_DIR) && corepack pnpm test

seed:
	cd $(API_DIR) && ../$(API_VENV)/bin/python scripts/seed_data.py

migrate:
	$(MAKE) -C $(API_DIR) migrate
