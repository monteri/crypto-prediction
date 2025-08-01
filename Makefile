.PHONY: help start-kafka start-app stop clean bootstrap test

help:
	@echo "Available commands:"
	@echo "  start-kafka    - Start Kafka infrastructure (kafka.yaml)"
	@echo "  start-app      - Start application services (compose.yml)"
	@echo "  start-all      - Start both Kafka and application services"
	@echo "  bootstrap      - Run bootstrap manually"
	@echo "  stop          - Stop all services"
	@echo "  clean         - Stop and remove all containers and volumes"
	@echo "  test          - Run tests"

start-kafka:
	@echo "🚀 Starting Kafka infrastructure..."
	docker-compose -f kafka.yaml up -d

start-app:
	@echo "🚀 Starting application services..."
	docker-compose -f compose.yml up -d

start-all: start-kafka
	@echo "⏳ Waiting for Kafka to be ready..."
	@sleep 10
	@echo "🚀 Starting application services..."
	docker-compose -f compose.yml up -d

bootstrap:
	@echo "🔧 Running bootstrap manually..."
	docker-compose -f kafka.yaml -f compose.yml run --rm bootstrap

stop:
	@echo "🛑 Stopping all services..."
	docker-compose -f compose.yml down
	docker-compose -f kafka.yaml down

clean:
	@echo "🧹 Cleaning up all containers and volumes..."
	docker-compose -f compose.yml down -v --remove-orphans
	docker-compose -f kafka.yaml down -v --remove-orphans
	docker system prune -f

test:
	@echo "🧪 Running tests..."
	docker-compose -f compose.yml run --rm web python -m pytest tests/

