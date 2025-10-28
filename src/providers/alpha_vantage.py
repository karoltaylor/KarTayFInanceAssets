"""Alpha Vantage provider client."""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict
import time
import requests
from config import settings
from config.logging_config import get_logger


class AlphaVantageClient:
    """Client for Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.logger = get_logger(self.__class__.__name__)
        if not self.api_key:
            self.logger.warning("Alpha Vantage API key is not set. Set ALPHA_VANTAGE_API_KEY in .env")

    def _get(self, params: Dict[str, str]) -> Dict:
        """Perform a GET request with basic retry on 429/5xx."""
        params = {**params, "apikey": self.api_key}
        backoff = 1.0
        for attempt in range(4):
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if "Note" in data or "Information" in data:
                        # Rate limited
                        self.logger.info("Alpha Vantage rate limit; backing off...")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    return data
                if resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(backoff)
                backoff *= 2
        return {}

    def fetch_fx_daily(self, from_symbol: str, to_symbol: str) -> List[Dict]:
        """Fetch FX daily time series.

        Returns list of dicts with fields: date, open, high, low, close.
        """
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "outputsize": "full",
        }
        data = self._get(params)
        series_key = "Time Series FX (Daily)"
        if series_key not in data:
            return []
        series = []
        for date_str, values in data[series_key].items():
            series.append({
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
                "open": float(values.get("1. open", 0.0)),
                "high": float(values.get("2. high", 0.0)),
                "low": float(values.get("3. low", 0.0)),
                "close": float(values.get("4. close", 0.0)),
            })
        # Sort ascending by date
        series.sort(key=lambda x: x["date"])
        return series

    def fetch_equity_daily(self, symbol: str) -> List[Dict]:
        """Fetch daily adjusted equity time series.

        Returns list of dicts with fields: date, open, high, low, close, volume.
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
        }
        data = self._get(params)
        series_key = "Time Series (Daily)"
        if series_key not in data:
            # Some responses may use adjusted key
            series_key = "Time Series (Daily)"
        if series_key not in data:
            return []
        series = []
        for date_str, values in data[series_key].items():
            series.append({
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
                "open": float(values.get("1. open", 0.0)),
                "high": float(values.get("2. high", 0.0)),
                "low": float(values.get("3. low", 0.0)),
                "close": float(values.get("4. close", 0.0)),
                "volume": float(values.get("6. volume", values.get("5. volume", 0.0))),
            })
        series.sort(key=lambda x: x["date"])
        return series


