"""Unit tests for services."""

from datetime import datetime, timedelta

import pytest

from src.services import ExchangeRateService, GoldPriceService, InflationService, StockPriceService


@pytest.mark.unit
class TestExchangeRateService:
    """Tests for ExchangeRateService."""

    def test_service_initialization(self, mock_db):
        """Test service initialization."""
        service = ExchangeRateService(mock_db)
        assert service.collection.name == "exchange_rates"

    def test_get_start_date_no_data(self, mock_db):
        """Test get_start_date with no existing data."""
        service = ExchangeRateService(mock_db)
        start_date = service.get_start_date()

        # Should return date from HISTORICAL_YEARS ago
        expected_date = datetime.now() - timedelta(days=365 * 3)
        assert start_date.date() == expected_date.date()

    def test_get_start_date_with_data(self, mock_db, sample_exchange_rate):
        """Test get_start_date with existing data."""
        service = ExchangeRateService(mock_db)
        service.collection.insert_one(sample_exchange_rate)

        start_date = service.get_start_date({"from_currency": "USD", "to_currency": "PLN"})

        # Should return day after latest date
        expected_date = sample_exchange_rate["date"] + timedelta(days=1)
        assert start_date.date() == expected_date.date()

    def test_get_latest_rates_empty(self, mock_db):
        """Test get_latest_rates with empty database."""
        service = ExchangeRateService(mock_db)
        rates = service.get_latest_rates()
        assert rates == []


@pytest.mark.unit
class TestGoldPriceService:
    """Tests for GoldPriceService."""

    def test_service_initialization(self, mock_db):
        """Test service initialization."""
        service = GoldPriceService(mock_db)
        assert service.collection.name == "gold_prices"

    def test_get_latest_price_empty(self, mock_db):
        """Test get_latest_price with empty database."""
        service = GoldPriceService(mock_db)
        price = service.get_latest_price()
        assert price is None

    def test_get_latest_price_with_data(self, mock_db, sample_gold_price):
        """Test get_latest_price with data."""
        service = GoldPriceService(mock_db)
        service.collection.insert_one(sample_gold_price)

        price = service.get_latest_price()
        assert price is not None
        assert price["price_usd"] == 1975.50


@pytest.mark.unit
class TestStockPriceService:
    """Tests for StockPriceService."""

    def test_service_initialization(self, mock_db):
        """Test service initialization."""
        service = StockPriceService(mock_db)
        assert service.collection.name == "stock_prices"

    def test_get_latest_price_empty(self, mock_db):
        """Test get_latest_price with empty database."""
        service = StockPriceService(mock_db)
        price = service.get_latest_price("^GSPC")
        assert price is None

    def test_get_latest_price_with_data(self, mock_db, sample_stock_price):
        """Test get_latest_price with data."""
        service = StockPriceService(mock_db)
        service.collection.insert_one(sample_stock_price)

        price = service.get_latest_price("^GSPC")
        assert price is not None
        assert price["close_price"] == 4510.00


@pytest.mark.unit
class TestInflationService:
    """Tests for InflationService."""

    def test_service_initialization(self, mock_db):
        """Test service initialization."""
        service = InflationService(mock_db)
        assert service.collection.name == "inflation_rates"

    def test_add_inflation_rate(self, mock_db):
        """Test adding a single inflation rate."""
        service = InflationService(mock_db)
        result = service.add_inflation_rate(date=datetime(2024, 10, 1), currency="USD", rate=3.2)
        assert result is True

    def test_get_latest_rate_empty(self, mock_db):
        """Test get_latest_rate with empty database."""
        service = InflationService(mock_db)
        rate = service.get_latest_rate("USD")
        assert rate is None

    def test_get_latest_rate_with_data(self, mock_db, sample_inflation_rate):
        """Test get_latest_rate with data."""
        service = InflationService(mock_db)
        service.collection.insert_one(sample_inflation_rate)

        rate = service.get_latest_rate("USD")
        assert rate is not None
        assert rate["rate"] == 3.2
