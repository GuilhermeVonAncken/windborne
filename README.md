# Alphavantage Financial ETL + Streamlit Dashboard

## Overview

This repository contains a full end-to-end prototype to:
- Fetch annual financial statements from Alpha Vantage for public companies
- Normalize and store them in PostgreSQL
- Compute a set of financial metrics and store them
- Provide a Streamlit dashboard to explore metrics
- Productionization guidance (n8n, scheduling, rate-limit strategies)

The repo is intentionally simple and designed for local development and quick deployment.

## Quick file map

- `src/` - Python source code
- `docs/prod_design.md` - Productionization notes, mermaid diagrams, n8n flow
- `docker-compose.yml` - Postgres + Streamlit for local dev
- `Dockerfile` - For building the app container
- `requirements.txt` - Python deps
- `.env.example` - example env vars
- `README.md` - this file

## Quick start (local)

1. Copy `.env.example` to `.env` and set `ALPHAVANTAGE_KEY`.
2. Start Postgres (recommended with docker-compose): `docker-compose up -d db`
3. Install Python deps: `pip install -r requirements.txt`
4. Run the loader to fetch data:
   ```
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finance_db
   export ALPHAVANTAGE_KEY=YOUR_KEY
   python -m src.loader
   ```
5. Compute metrics:
   ```
   python -c "from src.metrics import compute_for_all_companies; compute_for_all_companies()"
   ```
6. Start Streamlit:
   ```
   streamlit run src/streamlit_app.py
   ```

## Deployment

- Streamlit Cloud / Render are both good options.
- Use the `Dockerfile` + `docker-compose.yml` for a containerized deployment.

## Notes

- The project uses Alpha Vantage free tier limits (5 calls/min, 25 calls/day). For many tickers you must implement staggering or get a commercial data source.
- This repo stores raw API responses in `.cache/` to avoid repeated calls during development.
