set shell := ["/bin/bash", "-c"]

export PYTHONPATH := "app"

# Default task runs verification suite
default: verify

# Install runtime and dev dependencies
install:
	python3 -m pip install -r requirements.txt -r requirements.dev.txt

# Launch local development server
serve:
	uvicorn app.main:app --reload --port ${PORT-8010}

# Format source files with Ruff
format:
	python3 -m ruff format app

# Lint backend source
lint:
	python3 -m ruff check app

# Run test suite
pytest:
	python3 -m pytest --asyncio-mode=auto

# Aggregate lint + tests
verify: lint pytest

# Seed local database (idempotent defaults)
seed:
	python3 scripts/seed_users.py
	python3 scripts/seed_jobs.py
	python3 scripts/seed_candidate_workflow.py
	python3 scripts/seed_recruiters.py

# Create a filled draft PR via GitHub CLI
pr-draft:
	gh pr create --draft --fill
