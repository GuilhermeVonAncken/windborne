from datetime import datetime
from decimal import Decimal

def parse_amount(x):
    if x is None:
        return None
    try:
        return Decimal(x)
    except Exception:
        try:
            return Decimal(str(x).replace(',', ''))
        except Exception:
            return None

def flatten_annual_reports(company_id, statement_type, av_json):
    rows = []
    if av_json is None:
        return rows
    reports = av_json.get("annualReports", [])
    for r in reports:
        fiscal = r.get("fiscalDateEnding")
        for k, v in r.items():
            if k == "fiscalDateEnding":
                continue
            rows.append({
                "company_id": company_id,
                "statement_type": statement_type,
                "fiscal_date": datetime.strptime(fiscal, "%Y-%m-%d").date() if fiscal else None,
                "period_type": "annual",
                "key": k,
                "value": parse_amount(v),
                "raw_value_text": v
            })
    return rows
