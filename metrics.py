from decimal import Decimal
from collections import defaultdict
from src.models import SessionLocal, FinancialStatement, FinancialMetric, Company

def metric_safe_div(n, d):
    if n is None or d is None:
        return None
    try:
        if Decimal(d) == 0:
            return None
        return Decimal(n) / Decimal(d)
    except Exception:
        return None

def compute_for_company(company_id):
    session = SessionLocal()
    rows = session.query(FinancialStatement).filter_by(company_id=company_id).all()
    data = defaultdict(dict)
    for r in rows:
        key = (r.fiscal_date)
        data[key][r.key] = r.value

    fiscal_dates = sorted(data.keys())
    for i, fiscal in enumerate(fiscal_dates):
        d = data[fiscal]
        rev = d.get("totalRevenue")
        gross = d.get("grossProfit")
        opinc = d.get("operatingIncome")
        net = d.get("netIncome")
        cur_assets = d.get("totalCurrentAssets")
        cur_liab = d.get("totalCurrentLiabilities")

        gross_margin = metric_safe_div(gross, rev)
        op_margin = metric_safe_div(opinc, rev)
        net_margin = metric_safe_div(net, rev)
        current_ratio = metric_safe_div(cur_assets, cur_liab)

        if i>0:
            prev_rev = data[fiscal_dates[i-1]].get("totalRevenue")
            try:
                revenue_yoy = metric_safe_div((rev - prev_rev), prev_rev) if prev_rev is not None and rev is not None else None
            except Exception:
                revenue_yoy = None
        else:
            revenue_yoy = None

        metrics = {
            "Gross Margin %": gross_margin,
            "Operating Margin %": op_margin,
            "Net Margin %": net_margin,
            "Current Ratio": current_ratio,
            "Revenue YoY %": revenue_yoy
        }

        for name, value in metrics.items():
            existing = session.query(FinancialMetric).filter_by(company_id=company_id, fiscal_date=fiscal, metric_name=name).first()
            if existing:
                existing.metric_value = value
            else:
                fm = FinancialMetric(company_id=company_id, fiscal_date=fiscal, metric_name=name, metric_value=value)
                session.add(fm)
        session.commit()
    session.close()

def compute_for_all_companies():
    session = SessionLocal()
    companies = session.query(Company).all()
    for c in companies:
        compute_for_company(c.id)
    session.close()
