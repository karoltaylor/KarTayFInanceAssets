"""Database module for MongoDB operations."""
from .connection import get_database, close_database_connection
from .models import (
    ExchangeRate,
    InflationRate,
    GoldPrice,
    StockPrice
)

__all__ = [
    "get_database",
    "close_database_connection",
    "ExchangeRate",
    "InflationRate",
    "GoldPrice",
    "StockPrice"
]

