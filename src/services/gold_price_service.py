"""Service for fetching and storing gold price data."""

from datetime import datetime
from typing import List

from pymongo.database import Database

from src.database.models import GoldPrice
from src.providers.fred import FredClient

from .base_service import BaseDataService


class GoldPriceService(BaseDataService):
    """Service for managing gold price data."""

    # FRED London Bullion Market Association Gold Price PM (USD)
    # Series ID: GOLDPMGBD228NLBM
    FRED_SERIES_ID = "GOLDPMGBD228NLBM"

    def __init__(self, db: Database):
        """Initialize gold price service."""
        super().__init__(db, "gold_prices")
        self.client = FredClient()
        self.create_indexes([[("date", 1)]])

    def fetch_gold_prices(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        Fetch gold price data from FRED (London PM fix in USD).

        Args:
            start_date: Start date for data
            end_date: End date for data

        Returns:
            List of gold price records
        """
        try:
            self.logger.info(
                f"Fetching gold prices from {start_date.date()} to {end_date.date()} via FRED ({self.FRED_SERIES_ID})"
            )

            series = self.client.fetch_series_daily(self.FRED_SERIES_ID, start_date, end_date)
            if not series:
                self.logger.warning("No gold price data returned from FRED")
                return []

            records: List[dict] = []
            for item in series:
                ts: datetime = item["date"]
                price = item["close"]
                record = GoldPrice(date=ts, price_usd=float(price), source="fred")
                records.append(record.model_dump())

            self.logger.info(f"Fetched {len(records)} gold price records")
            return records

        except Exception as e:
            self.logger.error(f"Error fetching gold prices: {str(e)}")
            return []

    def update_gold_prices(self) -> dict:
        """
        Update gold prices with latest data.

        Returns:
            Dictionary with update statistics
        """
        stats = {"total_inserted": 0}
        end_date = datetime.now()
        start_date = self.get_start_date()

        if start_date >= end_date:
            self.logger.info("Gold prices are up to date")
            return stats

        # Fetch and insert data
        records = self.fetch_gold_prices(start_date, end_date)

        if records:
            try:
                inserted = self.bulk_insert(records)
                stats["total_inserted"] = inserted
            except Exception as e:
                self.logger.error(f"Error inserting gold price data: {str(e)}")

        return stats

    def get_latest_price(self) -> dict:
        """
        Get the latest gold price.

        Returns:
            Latest gold price record or None
        """
        return self.collection.find_one(sort=[("date", -1)])
