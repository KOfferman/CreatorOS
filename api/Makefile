.PHONY: up down logs api worker web migrate dev

up:
	docker compose up --build

dev:
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh

down:
	docker compose down

logs:
	docker compose logs -f

api:
	docker compose up --build api

worker:
	docker compose up --build worker

web:
	docker compose up --build web

migrate:
	docker compose run --rm api sh -c "cd /workspace/shared/database && alembic upgrade head"
