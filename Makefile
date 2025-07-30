start:
	docker-compose -f compose.yml up

build:
	docker-compose -f compose.yml build

kafka:
	docker-compose -f kafka.yaml up

test-all:
	cd api && python tests/run_tests.py

