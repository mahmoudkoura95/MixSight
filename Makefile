.PHONY: help up down logs reset api web test typecheck lint format migrate migrate-down migrate-history

help:
	@echo "MixSight dev commands:"
	@echo "  make up         - start postgres + redis"
	@echo "  make down       - stop containers"
	@echo "  make logs       - tail container logs"
	@echo "  make reset      - destroy + recreate db volumes"
	@echo "  make api        - run FastAPI on :8000"
	@echo "  make web        - run Next.js on :3000"
	@echo "  make test       - run pytest"
	@echo "  make typecheck  - mypy (api)"
	@echo "  make lint       - ruff check (api)"
	@echo "  make format     - ruff format (api)"
	@echo "  make migrate    - alembic upgrade head"
	@echo "  make migrate-down       - alembic downgrade -1"
	@echo "  make migrate-history    - alembic history"
	@echo ""
	@echo "Equivalent pnpm scripts exist for Windows users; see package.json."

up:
	docker compose -f infra/docker/docker-compose.yml up -d

down:
	docker compose -f infra/docker/docker-compose.yml down

logs:
	docker compose -f infra/docker/docker-compose.yml logs -f

reset:
	docker compose -f infra/docker/docker-compose.yml down -v
	docker compose -f infra/docker/docker-compose.yml up -d

api:
	cd apps/api && uv run uvicorn mixsight.main:app --reload --port 8000

web:
	pnpm --filter @mixsight/web dev

test:
	cd apps/api && uv run pytest

typecheck:
	cd apps/api && uv run mypy src

lint:
	cd apps/api && uv run ruff check src

format:
	cd apps/api && uv run ruff format src

migrate:
	cd apps/api && uv run alembic upgrade head

migrate-down:
	cd apps/api && uv run alembic downgrade -1

migrate-history:
	cd apps/api && uv run alembic history
