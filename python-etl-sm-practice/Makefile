.PHONY: setup db preview etl api test
setup:
	python -m venv .venv && .venv/bin/pip install -r requirements.txt
db:
	docker compose up -d db
preview:
	python -m src.etl.preview
etl:
	python -m src.etl.pipeline
api:
	uvicorn src.api.main:app --reload --port 8000
test:
	pytest -q
