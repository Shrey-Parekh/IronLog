.PHONY: up down migrate seed test lint

up:
	docker-compose -f docker-compose.dev.yml up --build

down:
	docker-compose -f docker-compose.dev.yml down

migrate:
	docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

seed:
	docker-compose -f docker-compose.dev.yml exec backend python -m app.seed.seed_db

test:
	docker-compose -f docker-compose.dev.yml exec backend pytest tests/ -v

lint:
	docker-compose -f docker-compose.dev.yml exec backend ruff check app/
