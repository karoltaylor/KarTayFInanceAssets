"""Database module for MongoDB operations."""

from .connection import close_database_connection, get_database
from .models import ExchangeRate, GoldPrice, InflationRate, StockPrice

__all__ = ["get_database", "close_database_connection", "ExchangeRate", "InflationRate", "GoldPrice", "StockPrice"]
