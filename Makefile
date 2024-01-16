DOCKER = docker
COMPOSE = docker-compose -f docker-compose.yml

all: up

s:
	@echo "\033[1;33mStarting containers\033[0m"
	@docker-compose -f docker-compose.yml up -d --build
	@docker-compose up

up:
	@echo "\033[1;33mStarting containers\033[0m"
	@$(COMPOSE) up -d --build
	@$(DOCKER)-compose up

down:
	@echo "\033[1;33mStopping containers\033[0m"
	@$(DOCKER)-compose down

start:
	@echo "\033[1;33mStarting containers\033[0m"
	@$(DOCKER)-compose start

stop:
	@echo "\033[1;33mStopping containers\033[0m"
	@$(DOCKER)-compose stop

restart:
	@echo "\033[1;33mRestarting containers\033[0m"
	@$(DOCKER)-compose restart

clean:
	@echo "\033[1;33mCleaning containers\033[0m"
	@$(DOCKER)-compose down -v --rmi all --remove-orphans

fclean:
	@echo "\033[1;33mCleaning containers\033[0m"
	@$(DOCKER)-compose down -v
	@echo "\033[1;33mPruning Docker\033[0m"
	@$(DOCKER) system prune -a --force
	@echo "\033[1;33mRemoving Docker Volumes\033[0m"
	@$(DOCKER) volume prune --force

status:
	@echo "\n\033[1;33mContainers\033[0m"
	@$(DOCKER) ps -a
	@echo "\n\033[1;33mImages\033[0m"
	@$(DOCKER) images
	@echo "\n\033[1;33mVolumes\033[0m"
	@$(DOCKER) volume ls
	@echo "\n\033[1;33mNetworks\033[0m"
	@$(DOCKER) network ls

daphne:
	($(COMPOSE) down daphne && $(COMPOSE) up daphne) || ($(COMPOSE) down daphne || $(COMPOSE) up daphne)

