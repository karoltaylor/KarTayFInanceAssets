"""Service for fetching and storing exchange rate data."""
from datetime import datetime
from typing import List
from pymongo.database import Database
from .base_service import BaseDataService
from src.database.models import ExchangeRate
from src.providers.fred import FredClient
from src.providers.nbp import NbpClient


class ExchangeRateService(BaseDataService):
    """Service for managing exchange rate data."""

    # Currency pairs to fetch
    CURRENCY_PAIRS = [
        ("USD", "PLN"),
        ("USD", "EUR"),
        ("EUR", "PLN"),
    ]

    def __init__(self, db: Database):
        """Initialize exchange rate service."""
        super().__init__(db, "exchange_rates")
        self.fred = FredClient()
        self.nbp = NbpClient()
        self.create_indexes([
            [("date", 1), ("from_currency", 1), ("to_currency", 1)]
        ])

    def fetch_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """Fetch exchange rate data using FRED (USD/EUR) or NBP (PLN pairs)."""
        try:
            self.logger.info(
                f"Fetching {from_currency}/{to_currency} from {start_date.date()} to {end_date.date()}"
            )

            records: List[dict] = []

            # If pair involves PLN, use NBP.
            if "PLN" in (from_currency, to_currency):
                # NBP returns PLN per 1 foreign currency (mid). If from=USD,to=PLN, rate = mid (PLN per 1 USD).
                # If from=PLN,to=USD (not used here), we'd invert.
                other = to_currency if from_currency == "PLN" else from_currency
                series = self.nbp.fetch_pln_rates(other, start_date, end_date)
                if not series:
                    self.logger.warning(f"No NBP data for {other}/PLN")
                    return []
                for item in series:
                    ts = item["date"]
                    mid = item["mid"]
                    if from_currency == "PLN" and to_currency != "PLN":
                        rate = 1.0 / mid  # PLN->USD/EUR
                    else:
                        rate = mid  # USD/EUR -> PLN
                    rec = ExchangeRate(
                        date=ts,
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=float(rate),
                        source="nbp"
                    )
                    records.append(rec.model_dump())
                self.logger.info(f"Fetched {len(records)} records for {from_currency}/{to_currency} via NBP")
                return records

            # Otherwise handle FRED for USD/EUR (DEXUSEU = USD per 1 EUR)
            pair = (from_currency, to_currency)
            if pair == ("USD", "EUR"):
                series = self.fred.fetch_series_daily("DEXUSEU", start_date, end_date)
                for item in series:
                    rec = ExchangeRate(
                        date=item["date"],
                        from_currency="USD",
                        to_currency="EUR",
                        rate=float(item["close"]),
                        source="fred"
                    )
                    records.append(rec.model_dump())
                self.logger.info(f"Fetched {len(records)} records for USD/EUR via FRED")
                return records
            elif pair == ("EUR", "USD"):
                series = self.fred.fetch_series_daily("DEXUSEU", start_date, end_date)
                for item in series:
                    val = item["close"]
                    if val and val != 0:
                        rate = 1.0 / float(val)
                        rec = ExchangeRate(
                            date=item["date"],
                            from_currency="EUR",
                            to_currency="USD",
                            rate=rate,
                            source="fred"
                        )
                        records.append(rec.model_dump())
                self.logger.info(f"Fetched {len(records)} records for EUR/USD via FRED (inverted DEXUSEU)")
                return records
            else:
                self.logger.warning(f"No provider configured for {from_currency}/{to_currency}")
                return []

        except Exception as e:
            self.logger.error(f"Error fetching {from_currency}/{to_currency}: {str(e)}")
            return []

    def update_all_pairs(self) -> dict:
        """
        Update all currency pairs with latest data.
        
        Returns:
            Dictionary with update statistics
        """
        stats = {"total_inserted": 0, "pairs_updated": 0}
        end_date = datetime.now()

        for (from_curr, to_curr) in self.CURRENCY_PAIRS:
            # Get start date for this specific pair
            start_date = self.get_start_date({
                "from_currency": from_curr,
                "to_currency": to_curr
            })

            if start_date >= end_date:
                self.logger.info(f"{from_curr}/{to_curr} is up to date")
                continue

            # Fetch and insert data
            records = self.fetch_exchange_rate(from_curr, to_curr, start_date, end_date)
            
            if records:
                try:
                    inserted = self.bulk_insert(records)
                    stats["total_inserted"] += inserted
                    stats["pairs_updated"] += 1
                except Exception as e:
                    self.logger.error(f"Error inserting {from_curr}/{to_curr} data: {str(e)}")

        return stats

    def get_latest_rates(self) -> List[dict]:
        """
        Get the latest exchange rates for all pairs.
        
        Returns:
            List of latest exchange rates
        """
        latest_rates = []
        
        for (from_curr, to_curr) in self.CURRENCY_PAIRS.keys():
            latest = self.collection.find_one(
                {"from_currency": from_curr, "to_currency": to_curr},
                sort=[("date", -1)]
            )
            if latest:
                latest_rates.append(latest)
        
        return latest_rates

