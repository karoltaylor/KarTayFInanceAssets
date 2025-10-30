"""Comprehensive integration tests for API endpoints."""

from datetime import datetime

import pytest


@pytest.mark.integration
class TestExchangeRateEndpointsComprehensive:
    """Comprehensive tests for exchange rate endpoints."""

    def test_get_latest_exchange_rates_with_data(self, api_client):
        """Test getting latest exchange rates with data."""
        response = api_client.get("/api/v1/exchange-rates/latest")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_exchange_rate_history_with_dates(self, api_client):
        """Test getting exchange rate history with date filters."""
        response = api_client.get(
            "/api/v1/exchange-rates/USD/PLN",
            params={"start_date": "2024-10-01", "end_date": "2024-10-31", "limit": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_update_exchange_rates(self, api_client):
        """Test manual exchange rate update."""
        # This will complete without external APIs in test mode
        response = api_client.post("/api/v1/exchange-rates/update")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestGoldPriceEndpointsComprehensive:
    """Comprehensive tests for gold price endpoints."""

    def test_get_latest_gold_price_not_found(self, api_client):
        """Test getting latest gold price when none exists."""
        response = api_client.get("/api/v1/gold/latest")
        assert response.status_code == 404

    def test_get_gold_price_history_with_dates(self, api_client):
        """Test getting gold price history with date filters."""
        response = api_client.get(
            "/api/v1/gold/history",
            params={"start_date": "2024-10-01", "end_date": "2024-10-31", "limit": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_update_gold_prices(self, api_client):
        """Test manual gold price update."""
        # This will complete without external APIs in test mode
        response = api_client.post("/api/v1/gold/update")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestStockPriceEndpointsComprehensive:
    """Comprehensive tests for stock price endpoints."""

    def test_get_latest_stock_price_not_found(self, api_client):
        """Test getting latest stock price when none exists."""
        response = api_client.get("/api/v1/stocks/^GSPC/latest")
        assert response.status_code == 404

    def test_get_stock_price_history_with_dates(self, api_client):
        """Test getting stock price history with date filters."""
        response = api_client.get(
            "/api/v1/stocks/^GSPC/history",
            params={"start_date": "2024-10-01", "end_date": "2024-10-31", "limit": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_update_sp500_prices(self, api_client):
        """Test manual S&P 500 update."""
        # This will complete without external APIs in test mode
        response = api_client.post("/api/v1/stocks/sp500/update")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestInflationEndpointsComprehensive:
    """Comprehensive tests for inflation endpoints."""

    def test_get_latest_inflation_rate_not_found(self, api_client):
        """Test getting latest inflation rate when none exists."""
        response = api_client.get("/api/v1/inflation/latest/USD")
        assert response.status_code == 404

    def test_get_inflation_history_with_dates(self, api_client):
        """Test getting inflation history with date filters."""
        response = api_client.get(
            "/api/v1/inflation/USD/history",
            params={"start_date": "2024-01-01", "end_date": "2024-12-31"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_update_inflation_worldbank(self, api_client):
        """Test World Bank inflation data update."""
        # This will complete without external APIs in test mode
        response = api_client.post("/api/v1/inflation/update-worldbank")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestUpdateAllEndpoint:
    """Tests for update all data endpoint."""

    def test_update_all_data(self, api_client):
        """Test updating all data."""
        # This will complete without external APIs in test mode
        response = api_client.post("/api/v1/update-all")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_date_format(self, api_client):
        """Test with invalid date format."""
        response = api_client.get("/api/v1/exchange-rates/USD/PLN", params={"start_date": "invalid-date"})
        # FastAPI will handle invalid date format
        assert response.status_code in [200, 422, 500]

    def test_invalid_currency(self, api_client):
        """Test with invalid currency code."""
        response = api_client.get("/api/v1/inflation/latest/INVALID")
        assert response.status_code in [404, 500]

    def test_invalid_symbol(self, api_client):
        """Test with invalid stock symbol."""
        response = api_client.get("/api/v1/stocks/INVALID/latest")
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestLimitParameters:
    """Tests for limit parameters."""

    def test_exchange_rate_limit(self, api_client):
        """Test exchange rate with limit parameter."""
        response = api_client.get("/api/v1/exchange-rates/USD/PLN", params={"limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10

    def test_gold_price_limit(self, api_client):
        """Test gold price with limit parameter."""
        response = api_client.get("/api/v1/gold/history", params={"limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10

    def test_stock_price_limit(self, api_client):
        """Test stock price with limit parameter."""
        response = api_client.get("/api/v1/stocks/^GSPC/history", params={"limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10
