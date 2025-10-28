"""Services module for data fetching and processing."""
from .exchange_rate_service import ExchangeRateService
from .inflation_service import InflationService
from .gold_price_service import GoldPriceService
from .stock_price_service import StockPriceService

__all__ = [
    "ExchangeRateService",
    "InflationService",
    "GoldPriceService",
    "StockPriceService"
]

