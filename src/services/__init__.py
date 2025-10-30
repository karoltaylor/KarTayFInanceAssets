"""Services module for data fetching and processing."""

from .exchange_rate_service import ExchangeRateService
from .gold_price_service import GoldPriceService
from .inflation_service import InflationService
from .stock_price_service import StockPriceService

__all__ = ["ExchangeRateService", "InflationService", "GoldPriceService", "StockPriceService"]
