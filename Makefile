COMPOSE := docker compose
SCRAPER_DIR := services/scraper
SCRAPER_HEALTH_URL := http://scraper:8000/health

.DEFAULT_GOAL := help

.PHONY: help setup up start down stop restart build rebuild pull ps logs logs-n8n logs-scraper logs-postgres health scraper-health config test scraper-dev scraper-shell n8n-shell clean clean-volumes

help:
	@echo "n8n job scraper commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          Create .env if missing and install scraper deps with uv"
	@echo ""
	@echo "Stack:"
	@echo "  make up             Build and start n8n, postgres, and scraper"
	@echo "  make start          Start existing containers"
	@echo "  make down           Stop and remove containers"
	@echo "  make stop           Stop containers without removing them"
	@echo "  make restart        Restart containers"
	@echo "  make build          Build the scraper image"
	@echo "  make rebuild        Rebuild scraper image without cache"
	@echo "  make pull           Pull n8n and postgres images"
	@echo "  make ps             Show container status"
	@echo "  make config         Validate and print compose config"
	@echo ""
	@echo "Logs and health:"
	@echo "  make logs           Follow all service logs"
	@echo "  make logs-n8n       Follow n8n logs"
	@echo "  make logs-scraper   Follow scraper logs"
	@echo "  make logs-postgres  Follow postgres logs"
	@echo "  make health         Check scraper health from inside n8n"
	@echo "  make scraper-health Check scraper health from inside scraper"
	@echo ""
	@echo "Scraper development:"
	@echo "  make test           Run scraper tests with uv"
	@echo "  make scraper-dev    Run scraper locally on port 8000"
	@echo "  make scraper-shell  Open a shell in the scraper container"
	@echo "  make n8n-shell      Open a shell in the n8n container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Stop containers and remove orphans"
	@echo "  make clean-volumes  Remove containers and named volumes"

setup:
	@test -f .env || cp .env.example .env
	cd $(SCRAPER_DIR) && uv sync

up:
	$(COMPOSE) up -d --build

start:
	$(COMPOSE) start

down:
	$(COMPOSE) down

stop:
	$(COMPOSE) stop

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build scraper

rebuild:
	$(COMPOSE) build --no-cache scraper

pull:
	$(COMPOSE) pull n8n postgres

ps:
	$(COMPOSE) ps

config:
	$(COMPOSE) config

logs:
	$(COMPOSE) logs -f

logs-n8n:
	$(COMPOSE) logs -f n8n

logs-scraper:
	$(COMPOSE) logs -f scraper

logs-postgres:
	$(COMPOSE) logs -f postgres

health:
	$(COMPOSE) exec -T n8n node -e "fetch('$(SCRAPER_HEALTH_URL)').then(r => r.text()).then(t => console.log(t))"

scraper-health:
	$(COMPOSE) exec -T scraper python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read().decode())"

test:
	cd $(SCRAPER_DIR) && uv run pytest

scraper-dev:
	cd $(SCRAPER_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

scraper-shell:
	$(COMPOSE) exec scraper sh

n8n-shell:
	$(COMPOSE) exec n8n sh

clean:
	$(COMPOSE) down --remove-orphans

clean-volumes:
	$(COMPOSE) down --volumes --remove-orphans
