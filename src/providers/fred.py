"""FRED (Federal Reserve Economic Data) provider client."""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict
import time
import requests
from config import settings
from config.logging_config import get_logger


class FredClient:
    """Client for FRED API.

    Docs: https://fred.stlouisfed.org/
    API: https://fred.stlouisfed.org/docs/api/fred/
    """

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    # Common FX series IDs
    SERIES_IDS = {
        # USD per EUR (U.S. Dollars to One Euro)
        ("USD", "EUR"): "DEXUSEU",  # series returns USD per 1 EUR
        # Note: For EUR->USD inversions, handle in service if needed
    }

    def __init__(self):
        self.api_key = settings.fred_api_key
        self.logger = get_logger(self.__class__.__name__)
        if not self.api_key:
            self.logger.warning("FRED API key is not set. Set FRED_API_KEY in .env")

    def fetch_series_daily(self, series_id: str, start: datetime, end: datetime) -> List[Dict]:
        """Fetch daily observations for a given series between start and end dates."""
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "frequency": "d",
        }

        backoff = 1.0
        for attempt in range(4):
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    observations = data.get("observations", [])
                    series: List[Dict] = []
                    for obs in observations:
                        date_str = obs.get("date")
                        value_str = obs.get("value")
                        # FRED uses "." for missing values
                        if not value_str or value_str == ".":
                            continue
                        try:
                            ts = datetime.strptime(date_str, "%Y-%m-%d")
                            val = float(value_str)
                        except Exception:
                            continue
                        series.append({"date": ts, "close": val})
                    return series
                if resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(backoff)
                backoff *= 2
        return []


