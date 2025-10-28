"""World Bank API provider for inflation data."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import requests

from config.logging_config import get_logger


class WorldBankClient:
    """Client for the World Bank API v2."""

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def fetch_inflation_cpi_annual(self, country_code: str, per_page: int = 2000) -> List[Dict]:
        """Fetch annual CPI inflation (consumer prices, annual %) for a country.

        Indicator: FP.CPI.TOTL.ZG

        Returns list of dicts with: year (int), value (float|None)
        """
        url = f"{self.BASE_URL}/country/{country_code}/indicator/FP.CPI.TOTL.ZG"
        params = {"format": "json", "per_page": per_page}

        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or len(data) < 2:
                return []
            observations = data[1] or []
            results: List[Dict] = []
            for obs in observations:
                year_str = obs.get("date")
                value = obs.get("value")
                try:
                    year = int(year_str)
                except Exception:
                    continue
                results.append({"year": year, "value": value})
            # Sort ascending by year
            results.sort(key=lambda x: x["year"])
            return results
        except Exception as e:
            self.logger.error(f"WorldBank fetch failed for {country_code}: {str(e)}")
            return []
