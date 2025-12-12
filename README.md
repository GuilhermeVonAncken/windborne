# Alphavantage Financial ETL + Streamlit Dashboard

## Requirements
- Python 3.10+
- Docker & Docker Compose (optional)
- Alpha Vantage API key (free tier)

## Quick start (local python)
1. pip install -r requirements.txt
2. Set env vars:
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finance_db
   export ALPHAVANTAGE_KEY=YOUR_KEY
3. Start Postgres (docker recommended):
   docker run --name finance-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=finance_db -p 5432:5432 -d postgres
4. Run loader:
   python -m src.loader
5. Compute metrics:
   python -c "from src.metrics import compute_for_company; from src.models import SessionLocal; s=SessionLocal(); from src.models import Company; ids=[c.id for c in s.query(Company).all()]; [compute_for_company(i) for i in ids];"
6. Start Streamlit:
   streamlit run src/streamlit_app.py

## Docker Compose
1. Create `.env` with ALPHAVANTAGE_KEY
2. docker-compose up --build
3. Streamlit available at http://localhost:8501

## Deployment
- Streamlit Cloud: push repo and set ALPHAVANTAGE_KEY secret; run streamlit_app.py
- Render: create web service pointing to streamlit run command.
