.PHONY: setup ingest features train predict dashboard test lint format logs stop clean full generate-data

setup:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pre-commit install

generate-data:
	python scripts/generate_sample.py

ingest: generate-data
	@mkdir -p data
	docker compose run --rm zeek bash -c "cd /data && zeek -r sample.pcap /zeek_scripts/extract_flows.zeek" 2>/dev/null || true
	python -m src.ingestion.pcap_to_parquet

features:
	python -m src.features.build_features

train:
	python -m src.models.train

predict:
	python -m src.models.predict

dashboard:
	docker compose up -d streamlit grafana
	@echo "Streamlit: http://localhost:8501"
	@echo "Grafana:   http://localhost:3000 (admin/admin)"

test:
	.venv/bin/pytest tests/ -v

lint:
	.venv/bin/ruff check src/ tests/
	.venv/bin/black --check src/ tests/

format:
	.venv/bin/black src/ tests/
	.venv/bin/ruff check --fix src/ tests/

logs:
	docker compose logs -f

stop:
	docker compose down

clean:
	docker compose down -v
	rm -rf .venv
	rm -rf data/*.parquet
	rm -rf data/*.csv
	rm -rf src/models/*.pkl
	rm -rf src/models/model_card.md

full: setup ingest features train dashboard