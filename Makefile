start:
	docker compose up
start-build:
	docker compose up --build
stop:
	docker compose down
restart:
	docker compose down && docker compose up --build
