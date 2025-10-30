"""MongoDB models for financial data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExchangeRate(BaseModel):
    """Exchange rate data model."""

    date: datetime
    from_currency: str = Field(..., description="Source currency code (e.g., USD)")
    to_currency: str = Field(..., description="Target currency code (e.g., PLN)")
    rate: float = Field(..., description="Exchange rate")
    source: str = Field(default="yfinance", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-10-20T00:00:00",
                "from_currency": "USD",
                "to_currency": "PLN",
                "rate": 3.95,
                "source": "yfinance",
            }
        }


class InflationRate(BaseModel):
    """Inflation rate data model."""

    date: datetime
    currency: str = Field(..., description="Currency code (e.g., USD, PLN, EUR)")
    rate: float = Field(..., description="Inflation rate as percentage")
    source: str = Field(default="manual", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {"date": "2024-10-01T00:00:00", "currency": "USD", "rate": 3.2, "source": "manual"}
        }


class GoldPrice(BaseModel):
    """Gold price data model."""

    date: datetime
    price_usd: float = Field(..., description="Gold price in USD per ounce")
    source: str = Field(default="yfinance", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {"example": {"date": "2024-10-20T00:00:00", "price_usd": 1975.50, "source": "yfinance"}}


class StockPrice(BaseModel):
    """Stock/Index price data model."""

    date: datetime
    symbol: str = Field(..., description="Stock/Index symbol (e.g., ^GSPC for S&P 500)")
    open_price: Optional[float] = Field(None, description="Opening price")
    high_price: Optional[float] = Field(None, description="Highest price")
    low_price: Optional[float] = Field(None, description="Lowest price")
    close_price: float = Field(..., description="Closing price")
    volume: Optional[float] = Field(None, description="Trading volume")
    source: str = Field(default="yfinance", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {"date": "2024-10-20T00:00:00", "symbol": "^GSPC", "close_price": 4500.50, "source": "yfinance"}
        }
