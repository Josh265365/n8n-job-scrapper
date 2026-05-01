# n8n Job Scraper

Run an n8n workflow with a private FastAPI scraper service and PostgreSQL-backed n8n storage.

The stack is designed so only n8n is available from your browser. The scraper and database stay private on the Docker Compose network.

## What Runs

```text
localhost:5678  -> n8n editor
n8n container   -> http://scraper:8000/scrape
n8n container   -> postgres:5432
```

No scraper or Postgres ports are published to your host machine.

## Project Layout

```text
.
├── docker-compose.yml
├── Makefile
├── workflows/
│   └── job-search-workflow.json
└── services/
    └── scraper/
        ├── app/
        ├── tests/
        ├── Dockerfile
        ├── pyproject.toml
        └── uv.lock
```

## Prerequisites

- Docker Desktop
- `make`
- `uv`, only needed for local scraper development and tests

Install `uv` if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## First Run

From the repository root:

```bash
make setup
make up
```

The first scraper build can take a while because Docker installs Chromium headless shell for Playwright.

Check the containers:

```bash
make ps
```

Check that n8n can reach the scraper:

```bash
make health
```

Expected output:

```json
{"status":"healthy"}
```

Open n8n:

```text
http://localhost:5678
```

## Import The Workflow

1. Open n8n at `http://localhost:5678`.
2. Create your n8n owner account if this is the first run.
3. Import `workflows/job-search-workflow.json`.
4. Open the imported workflow.
5. Confirm the HTTP Request node URL is:

```text
http://scraper:8000/scrape
```

Do not change that URL to `localhost`. Inside n8n, `localhost` means the n8n container itself, not your host machine and not the scraper container.

## Configure The Workflow

The imported workflow includes placeholders that you need to fill in n8n:

- Google Docs node: choose the CV/resume document to read.
- Google Sheets node: choose the sheet where results should be appended or updated.
- OpenAI Chat Model node: add your OpenAI API key as an n8n credential, then choose the credential and model.
- HTTP Request node: adjust the job query, location, and limit if needed.

### OpenAI API Key

The workflow uses the n8n OpenAI Chat Model node. You need an OpenAI API key before that node can run.

In n8n:

1. Open **Credentials**.
2. Create a new **OpenAI API** credential.
3. Paste your OpenAI API key.
4. Save the credential.
5. Open the workflow's **OpenAI Chat Model** node.
6. Select the OpenAI credential and choose the model you want to use.

Do not put the OpenAI API key in the scraper `.env`; the scraper does not call OpenAI directly. n8n owns that credential.

Default scraper request body:

```json
{
  "site": "linkedin",
  "query": "Graduate Technology",
  "location": "United Kingdom",
  "limit": 10
}
```

The scraper currently supports LinkedIn only.

## Run The Workflow

In n8n:

1. Use the manual trigger to test the workflow.
2. Check the HTTP Request node output first.
3. Check the Split Out node to confirm job items are being split.
4. Check the AI Agent and Google Sheets nodes after credentials are configured.
5. Enable the schedule trigger only after a manual run works.

## Common Commands

```bash
make up              # build and start the full stack
make down            # stop and remove containers
make restart         # restart all services
make ps              # show container status
make logs            # follow all logs
make logs-n8n        # follow n8n logs
make logs-scraper    # follow scraper logs
make health          # test n8n -> scraper
make scraper-health  # test scraper health inside its own container
make test            # run scraper tests with uv
```

## Docker Networking

This Compose project contains three services:

- `n8n`
- `scraper`
- `postgres`

Compose creates a private Docker network for them. Services can reach each other by service name:

```text
http://scraper:8000
postgres:5432
```

Only n8n has a `ports` mapping:

```yaml
ports:
  - "${N8N_PORT:-5678}:5678"
```

The scraper uses `expose`, not `ports`:

```yaml
expose:
  - "8000"
```

That means other containers in the Compose project can use port `8000`, but your host machine cannot access it as `localhost:8000`.

## Environment

`make setup` creates `.env` from `.env.example` if `.env` does not exist.

Important values:

```env
N8N_PORT=5678
N8N_HOST=localhost
N8N_WEBHOOK_URL=http://localhost:5678/
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=change_me
SCRAPER_HEADLESS=true
SCRAPER_BROWSER=chromium
```

Change `POSTGRES_PASSWORD` before using this beyond local development.

## Local Scraper Development

Run the scraper outside Docker:

```bash
cd services/scraper
uv sync
uv run pytest
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test it from your host:

```bash
curl http://localhost:8000/health
```

Example scrape request:

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"site":"linkedin","query":"Graduate Technology","location":"United Kingdom","limit":10}'
```

Only use local scraper development if nothing else on your machine is already using port `8000`.

## Troubleshooting

If n8n cannot call the scraper, run:

```bash
make health
make logs-scraper
```

If `localhost:8000` does not work, that is expected in Docker mode. The scraper is intentionally private. Use `http://scraper:8000` from n8n.

If scraper logs show repeated `GET /health`, that is Docker checking whether the service is healthy. The interval is configured in `docker-compose.yml`.

If n8n starts but the workflow fails at Google or OpenAI nodes, configure the required n8n credentials and choose the target documents/sheets in those nodes.

If you want to fully reset n8n and Postgres data:

```bash
make clean-volumes
make up
```

This deletes the Docker volumes for n8n and Postgres.
