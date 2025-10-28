"""NBP (Narodowy Bank Polski) API provider for PLN exchange rates."""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict
import requests
from config.logging_config import get_logger


class NbpClient:
    """Client for the NBP API.

    Docs: http://api.nbp.pl/
    We'll use table A: mid rates PLN per 1 unit of foreign currency.
    Endpoint: /api/exchangerates/rates/A/{code}/{startDate}/{endDate}/?format=json
    """

    BASE_URL = "https://api.nbp.pl/api"

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def fetch_pln_rates(self, code: str, start: datetime, end: datetime) -> List[Dict]:
        """Fetch PLN rates for given currency code (e.g., USD, EUR) over date range.

        Returns list of dicts with: date, mid
        """
        url = f"{self.BASE_URL}/exchangerates/rates/A/{code}/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}" \
              + "/?format=json"
        try:
            resp = requests.get(url, timeout=30, headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()
            rates = data.get("rates", [])
            series: List[Dict] = []
            for r in rates:
                date_str = r.get("effectiveDate")
                mid = r.get("mid")
                if date_str is None or mid is None:
                    continue
                try:
                    ts = datetime.strptime(date_str, "%Y-%m-%d")
                    series.append({"date": ts, "mid": float(mid)})
                except Exception:
                    continue
            return series
        except Exception as e:
            self.logger.error(f"NBP fetch failed for {code}: {str(e)}")
            return []


