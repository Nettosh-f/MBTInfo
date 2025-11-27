.PHONY: help build up down logs clean push

# Variables
DOCKER_IMAGE=mbtinfo-backend
DOCKER_TAG=latest
AWS_REGION=us-east-1
ECR_REPO=mbtinfo-backend
ECR_URL=123456789012.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}

help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build:
	docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v
	docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true

# Local development
install: ## Install Python dependencies
	pip install -r backend/requirements.txt

# Code quality
lint:
	ruff check backend/

lint-fix:
	ruff check --fix backend/

format:
	black backend/

format-check:
	black --check backend/

check: lint format-check

