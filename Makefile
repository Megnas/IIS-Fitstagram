.PHONY: run rebuild stop

run: .env
	docker-compose up -d

rebuild: .env
	docker-compose up -d rebuild web

.env: env_example
	[ ! -f .env ] && cp env_example .env

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -f .env

