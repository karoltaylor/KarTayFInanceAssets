"""Unit tests for database models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.database.models import ExchangeRate, GoldPrice, InflationRate, StockPrice


class TestExchangeRateModel:
    """Tests for ExchangeRate model."""

    def test_valid_exchange_rate(self):
        """Test creating a valid exchange rate."""
        rate = ExchangeRate(date=datetime(2024, 10, 20), from_currency="USD", to_currency="PLN", rate=3.95)
        assert rate.from_currency == "USD"
        assert rate.to_currency == "PLN"
        assert rate.rate == 3.95

    def test_exchange_rate_missing_fields(self):
        """Test exchange rate with missing required fields."""
        with pytest.raises(ValidationError):
            ExchangeRate(from_currency="USD")


class TestInflationRateModel:
    """Tests for InflationRate model."""

    def test_valid_inflation_rate(self):
        """Test creating a valid inflation rate."""
        rate = InflationRate(date=datetime(2024, 10, 1), currency="USD", rate=3.2)
        assert rate.currency == "USD"
        assert rate.rate == 3.2

    def test_inflation_rate_with_source(self):
        """Test inflation rate with custom source."""
        rate = InflationRate(date=datetime(2024, 10, 1), currency="EUR", rate=2.8, source="custom")
        assert rate.source == "custom"


class TestGoldPriceModel:
    """Tests for GoldPrice model."""

    def test_valid_gold_price(self):
        """Test creating a valid gold price."""
        price = GoldPrice(date=datetime(2024, 10, 20), price_usd=1975.50)
        assert price.price_usd == 1975.50
        assert price.source == "yfinance"


class TestStockPriceModel:
    """Tests for StockPrice model."""

    def test_valid_stock_price(self):
        """Test creating a valid stock price."""
        price = StockPrice(date=datetime(2024, 10, 20), symbol="^GSPC", close_price=4500.50)
        assert price.symbol == "^GSPC"
        assert price.close_price == 4500.50

    def test_stock_price_with_all_fields(self):
        """Test stock price with all fields."""
        price = StockPrice(
            date=datetime(2024, 10, 20),
            symbol="^GSPC",
            open_price=4490.00,
            high_price=4520.00,
            low_price=4480.00,
            close_price=4510.00,
            volume=1000000.0,
        )
        assert price.open_price == 4490.00
        assert price.volume == 1000000.0
