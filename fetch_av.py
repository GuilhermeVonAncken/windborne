import os, time, json, requests
from pathlib import Path

BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHAVANTAGE_KEY")

CACHE_DIR = Path("./.cache")
CACHE_DIR.mkdir(exist_ok=True)

class AlphaVantageClient:
    def __init__(self, api_key=None, calls_per_min=5):
        self.api_key = api_key or API_KEY
        self.calls_per_min = calls_per_min
        self.min_interval = 60.0 / self.calls_per_min
        self._last_call = 0.0

    def _rate_limit_sleep(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

    def _call(self, params, cache_key=None, max_retries=5):
        if cache_key:
            cache_file = CACHE_DIR / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    return json.loads(cache_file.read_text())
                except Exception:
                    pass

        retries = 0
        backoff = 1.0
        while retries < max_retries:
            self._rate_limit_sleep()
            resp = requests.get(BASE, params={**params, "apikey": self.api_key}, timeout=30)
            self._last_call = time.time()
            if resp.status_code == 200:
                try:
                    j = resp.json()
                except Exception:
                    j = None
                if j and ("Note" in j or "Error Message" in j):
                    raise RuntimeError(f"AlphaVantage response error: {j}")
                if cache_key and j is not None:
                    cache_file.write_text(json.dumps(j, default=str))
                return j
            elif resp.status_code in (429, 503):
                time.sleep(backoff)
                backoff *= 2
                retries += 1
            else:
                resp.raise_for_status()
        raise RuntimeError("Max retries exceeded for AlphaVantage call")

    def get_income_statement_annual(self, symbol):
        params = {"function": "INCOME_STATEMENT", "symbol": symbol}
        return self._call(params, cache_key=f"{symbol}_income")

    def get_balance_sheet_annual(self, symbol):
        params = {"function": "BALANCE_SHEET", "symbol": symbol}
        return self._call(params, cache_key=f"{symbol}_balance")

    def get_cash_flow_annual(self, symbol):
        params = {"function": "CASH_FLOW", "symbol": symbol}
        return self._call(params, cache_key=f"{symbol}_cashflow")
