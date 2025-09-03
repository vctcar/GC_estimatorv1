.PHONY: help build up down logs clean dev prod test

# Default target
help:
	@echo "Available commands:"
	@echo "  build    - Build all Docker images"
	@echo "  up       - Start all services in production mode"
	@echo "  down     - Stop all services"
	@echo "  logs     - View logs from all services"
	@echo "  clean    - Remove all containers, images, and volumes"
	@echo "  dev      - Start all services in development mode"
	@echo "  prod     - Start all services in production mode"
	@echo "  test     - Run tests"

# Build all images
build:
	docker-compose build

# Start production services
up:
	docker-compose up -d

# Start development services (uses override file automatically)
dev:
	docker-compose up --build

# Start production services (ignores override file)
prod:
	docker-compose -f docker-compose.yml up --build -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Run tests
test:
	docker-compose exec backend python -m pytest

# Backend specific commands
backend-logs:
	docker-compose logs -f backend

backend-shell:
	docker-compose exec backend bash

# Frontend specific commands
frontend-logs:
	docker-compose logs -f frontend

frontend-shell:
	docker-compose exec frontend sh
