.PHONY: test-unit test-psql dev dev-makeaplea dev-api dev-psql dev-exec stop rm

define container-id-for
	$(shell docker ps -f 'label=com.docker.compose.project=$(1)' -f 'label=com.docker.compose.service=$(2)' -q)
endef

test-unit: ## Run unit tests
	docker-compose -p test build test-unit
	docker-compose -p test run test-unit

test-psql: ## Run psql against the test database
	docker exec -ti -u postgres $(call container-id-for,test,postgres) psql makeaplea

dev: dev-makeaplea

dev-makeaplea: ## Run the makeaplea frontend app
	docker-compose -p dev build makeaplea
	docker-compose -p dev run -p $${PORT:-8000}:8000 makeaplea

dev-api: ## Run the makeaplea api app
	docker-compose -p dev build makeaplea_api
	docker-compose -p dev run -p $${PORT:-8001}:8000 makeaplea_api

dev-psql: ## Run psql against the dev datatabase
	docker exec -ti -u postgres $(call container-id-for,dev,postgres) psql makeaplea

dev-exec: ## Output the start of a docker exec against the makeaplea frontend app
	@echo docker exec -ti $(call container-id-for,dev,makeaplea)

stop: ## Stop all dev and test containers
	docker-compose -p dev stop
	docker-compose -p test stop

rm: ## Remove all dev and test containers
	docker-compose -p dev rm
	docker-compose -p test rm
