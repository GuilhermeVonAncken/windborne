import os
from src.fetch_av import AlphaVantageClient
from src.transform import flatten_annual_reports
from src.models import SessionLocal, create_schema, Company, FinancialStatement
from sqlalchemy.exc import IntegrityError

def upsert_company(session, ticker, name=None, exchange=None):
    company = session.query(Company).filter_by(ticker=ticker).first()
    if not company:
        company = Company(ticker=ticker, name=name, exchange=exchange)
        session.add(company)
        session.flush()
    return company

def persist_rows(session, rows):
    for r in rows:
        if r.get('fiscal_date') is None:
            continue
        fs = FinancialStatement(
            company_id = r["company_id"],
            statement_type = r["statement_type"],
            fiscal_date = r["fiscal_date"],
            period_type = r["period_type"],
            key = r["key"],
            value = r["value"],
            raw_value_text = r["raw_value_text"]
        )
        try:
            session.add(fs)
            session.commit()
        except IntegrityError:
            session.rollback()
            existing = session.query(FinancialStatement).filter_by(
                company_id=r["company_id"],
                statement_type=r["statement_type"],
                fiscal_date=r["fiscal_date"],
                period_type=r["period_type"],
                key=r["key"]
            ).first()
            if existing:
                existing.value = r["value"]
                existing.raw_value_text = r["raw_value_text"]
                session.commit()

def run_for_tickers(tickers):
    create_schema()
    client = AlphaVantageClient()
    session = SessionLocal()
    for ticker in tickers:
        company = upsert_company(session, ticker)
        # income
        inc = client.get_income_statement_annual(ticker)
        rows = flatten_annual_reports(company.id, "income", inc)
        persist_rows(session, rows)
        # balance
        bal = client.get_balance_sheet_annual(ticker)
        rows = flatten_annual_reports(company.id, "balance_sheet", bal)
        persist_rows(session, rows)
        # cashflow
        cf = client.get_cash_flow_annual(ticker)
        rows = flatten_annual_reports(company.id, "cashflow", cf)
        persist_rows(session, rows)
    session.close()

if __name__ == "__main__":
    tickers = ["TEL","ST","DD"]
    run_for_tickers(tickers)
