"""Comprehensive unit tests for services to increase coverage."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.services import (
    ExchangeRateService,
    GoldPriceService,
    InflationService,
    StockPriceService,
)
from src.services.base_service import BaseDataService


@pytest.mark.unit
class TestBaseDataService:
    """Tests for BaseDataService."""

    def test_get_latest_date_with_data(self, mock_db):
        """Test get_latest_date with existing data."""
        service = BaseDataService(mock_db, "test_collection")
        test_date = datetime(2024, 10, 20)
        service.collection.insert_one({"date": test_date, "value": 100})

        latest = service.get_latest_date()
        assert latest == test_date

    def test_get_latest_date_with_filter(self, mock_db):
        """Test get_latest_date with query filter."""
        service = BaseDataService(mock_db, "test_collection")
        test_date = datetime(2024, 10, 20)
        service.collection.insert_one({"date": test_date, "currency": "USD", "value": 100})
        service.collection.insert_one({"date": datetime(2024, 10, 21), "currency": "EUR", "value": 200})

        latest = service.get_latest_date({"currency": "USD"})
        assert latest == test_date

    def test_bulk_insert_empty(self, mock_db):
        """Test bulk_insert with empty list."""
        service = BaseDataService(mock_db, "test_collection")
        count = service.bulk_insert([])
        assert count == 0

    def test_bulk_insert_success(self, mock_db):
        """Test bulk_insert with records."""
        service = BaseDataService(mock_db, "test_collection")
        records = [{"date": datetime.now(), "value": i} for i in range(5)]
        count = service.bulk_insert(records)
        assert count == 5

    def test_create_indexes(self, mock_db):
        """Test create_indexes."""
        service = BaseDataService(mock_db, "test_collection")
        service.create_indexes([[("date", 1)]])
        # Should not raise exception


@pytest.mark.unit
class TestExchangeRateServiceComprehensive:
    """Comprehensive tests for ExchangeRateService."""

    def test_get_latest_rates_with_data(self, mock_db, sample_exchange_rate):
        """Test get_latest_rates with data."""
        service = ExchangeRateService(mock_db)
        service.collection.insert_one(sample_exchange_rate)

        rates = service.get_latest_rates()
        assert isinstance(rates, list)

    @patch("src.services.exchange_rate_service.FredClient")
    @patch("src.services.exchange_rate_service.NbpClient")
    def test_fetch_exchange_rate_nbp_pln_pair(self, mock_nbp_class, mock_fred_class, mock_db):
        """Test fetching PLN pair via NBP."""
        mock_nbp = Mock()
        mock_nbp.fetch_pln_rates.return_value = [{"date": datetime(2024, 10, 20), "mid": 3.95}]
        mock_nbp_class.return_value = mock_nbp

        service = ExchangeRateService(mock_db)
        service.nbp = mock_nbp

        records = service.fetch_exchange_rate("USD", "PLN", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert len(records) == 1
        assert records[0]["from_currency"] == "USD"
        assert records[0]["to_currency"] == "PLN"

    @patch("src.services.exchange_rate_service.FredClient")
    @patch("src.services.exchange_rate_service.NbpClient")
    def test_fetch_exchange_rate_fred_usd_eur(self, mock_nbp_class, mock_fred_class, mock_db):
        """Test fetching USD/EUR via FRED."""
        mock_fred = Mock()
        mock_fred.fetch_series_daily.return_value = [{"date": datetime(2024, 10, 20), "close": 0.92}]
        mock_fred_class.return_value = mock_fred

        service = ExchangeRateService(mock_db)
        service.fred = mock_fred

        records = service.fetch_exchange_rate("USD", "EUR", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert len(records) == 1
        assert records[0]["from_currency"] == "USD"
        assert records[0]["to_currency"] == "EUR"


@pytest.mark.unit
class TestGoldPriceServiceComprehensive:
    """Comprehensive tests for GoldPriceService."""

    @patch("src.services.gold_price_service.yfinance.Ticker")
    def test_fetch_gold_prices(self, mock_ticker_class, mock_db):
        """Test fetching gold prices."""
        mock_ticker = Mock()
        mock_history = Mock()
        mock_history.empty = False
        mock_history.iterrows.return_value = [(datetime(2024, 10, 20), {"Close": 1975.50})]
        mock_ticker.history.return_value = mock_history
        mock_ticker_class.return_value = mock_ticker

        service = GoldPriceService(mock_db)
        records = service.fetch_gold_prices(datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert len(records) > 0

    def test_update_gold_prices(self, mock_db):
        """Test update_gold_prices method."""
        service = GoldPriceService(mock_db)
        with patch.object(service, "fetch_gold_prices", return_value=[]):
            stats = service.update_gold_prices()
            assert "total_inserted" in stats


@pytest.mark.unit
class TestStockPriceServiceComprehensive:
    """Comprehensive tests for StockPriceService."""

    @patch("src.services.stock_price_service.yfinance.Ticker")
    def test_fetch_stock_prices(self, mock_ticker_class, mock_db):
        """Test fetching stock prices."""
        mock_ticker = Mock()
        mock_history = Mock()
        mock_history.empty = False
        mock_history.iterrows.return_value = [
            (
                datetime(2024, 10, 20),
                {"Open": 4500.0, "High": 4520.0, "Low": 4490.0, "Close": 4510.0, "Volume": 1000000.0},
            )
        ]
        mock_ticker.history.return_value = mock_history
        mock_ticker_class.return_value = mock_ticker

        service = StockPriceService(mock_db)
        records = service.fetch_stock_prices("^GSPC", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert len(records) > 0

    def test_update_sp500(self, mock_db):
        """Test update_sp500 method."""
        service = StockPriceService(mock_db)
        with patch.object(service, "fetch_stock_prices", return_value=[]):
            stats = service.update_sp500()
            assert "total_inserted" in stats


@pytest.mark.unit
class TestInflationServiceComprehensive:
    """Comprehensive tests for InflationService."""

    def test_get_rates_by_currency(self, mock_db, sample_inflation_rate):
        """Test get_rates_by_currency."""
        service = InflationService(mock_db)
        service.collection.insert_one(sample_inflation_rate)

        rates = service.get_rates_by_currency("USD")
        assert isinstance(rates, list)

    def test_get_rates_by_currency_with_dates(self, mock_db, sample_inflation_rate):
        """Test get_rates_by_currency with date range."""
        service = InflationService(mock_db)
        service.collection.insert_one(sample_inflation_rate)

        start = datetime(2024, 9, 1)
        end = datetime(2024, 11, 1)
        rates = service.get_rates_by_currency("USD", start, end)
        assert isinstance(rates, list)

    def test_seed_sample_data(self, mock_db):
        """Test seed_sample_data."""
        service = InflationService(mock_db)
        count = service.seed_sample_data()
        assert count > 0

    @patch("src.services.inflation_service.WorldBankClient")
    def test_update_inflation_from_world_bank(self, mock_wb_class, mock_db):
        """Test update_inflation_from_world_bank."""
        mock_wb = Mock()
        mock_wb.fetch_inflation_data.return_value = [{"date": datetime(2024, 1, 1), "value": 3.2}]
        mock_wb_class.return_value = mock_wb

        service = InflationService(mock_db)
        service.world_bank = mock_wb

        stats = service.update_inflation_from_world_bank()
        assert "countries_updated" in stats
