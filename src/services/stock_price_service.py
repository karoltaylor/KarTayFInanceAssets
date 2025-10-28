"""Service for fetching and storing stock/index price data."""
from datetime import datetime
from typing import List
from pymongo.database import Database
from .base_service import BaseDataService
from src.database.models import StockPrice
from src.providers.alpha_vantage import AlphaVantageClient


class StockPriceService(BaseDataService):
    """Service for managing stock/index price data."""

    # We'll fetch SPY ETF via Alpha Vantage as proxy for S&P 500
    SPY_SYMBOL = "SPY"

    def __init__(self, db: Database):
        """Initialize stock price service."""
        super().__init__(db, "stock_prices")
        self.client = AlphaVantageClient()
        self.create_indexes([[("date", 1), ("symbol", 1)]])

    def fetch_stock_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """
        Fetch stock/index price data from Yahoo Finance.
        
        Args:
            symbol: Stock or index symbol
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            List of stock price records
        """
        try:
            self.logger.info(f"Fetching {symbol} prices from {start_date.date()} to {end_date.date()} via Alpha Vantage")

            # Normalize to SPY if user passes ^GSPC
            av_symbol = self.SPY_SYMBOL if symbol.upper() in {"^GSPC", "GSPC", "SPY"} else symbol.upper()
            series = self.client.fetch_equity_daily(av_symbol)
            if not series:
                self.logger.warning(f"No data returned for {av_symbol}")
                return []

            records: List[dict] = []
            for item in series:
                ts: datetime = item["date"]
                if ts.date() < start_date.date() or ts.date() > end_date.date():
                    continue
                record = StockPrice(
                    date=ts,
                    symbol=av_symbol,
                    open_price=float(item["open"]) if item.get("open") is not None else None,
                    high_price=float(item["high"]) if item.get("high") is not None else None,
                    low_price=float(item["low"]) if item.get("low") is not None else None,
                    close_price=float(item["close"]),
                    volume=float(item["volume"]) if item.get("volume") is not None else None,
                    source="alphavantage"
                )
                records.append(record.model_dump())

            self.logger.info(f"Fetched {len(records)} records for {av_symbol}")
            return records

        except Exception as e:
            self.logger.error(f"Error fetching {symbol} prices: {str(e)}")
            return []

    def update_sp500(self) -> dict:
        """
        Update S&P 500 index data with latest prices.
        
        Returns:
            Dictionary with update statistics
        """
        stats = {"total_inserted": 0}
        end_date = datetime.now()
        start_date = self.get_start_date({"symbol": self.SPY_SYMBOL})

        if start_date >= end_date:
            self.logger.info("S&P 500 data is up to date")
            return stats

        # Fetch and insert data
        records = self.fetch_stock_prices(self.SPY_SYMBOL, start_date, end_date)
        
        if records:
            try:
                inserted = self.bulk_insert(records)
                stats["total_inserted"] = inserted
            except Exception as e:
                self.logger.error(f"Error inserting S&P 500 data: {str(e)}")

        return stats

    def get_latest_price(self, symbol: str) -> dict:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Stock or index symbol
            
        Returns:
            Latest price record or None
        """
        return self.collection.find_one(
            {"symbol": symbol},
            sort=[("date", -1)]
        )

