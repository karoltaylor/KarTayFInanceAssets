"""Integration tests for API endpoints."""
import pytest


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_root_endpoint(self, api_client):
        """Test root endpoint."""
        response = api_client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Finance Assets API"

    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.integration
class TestExchangeRateEndpoints:
    """Tests for exchange rate endpoints."""

    def test_get_latest_exchange_rates_empty(self, api_client):
        """Test getting latest exchange rates with empty database."""
        response = api_client.get("/api/v1/exchange-rates/latest")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_exchange_rate_history(self, api_client):
        """Test getting exchange rate history."""
        response = api_client.get("/api/v1/exchange-rates/USD/PLN")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


@pytest.mark.integration
class TestGoldPriceEndpoints:
    """Tests for gold price endpoints."""

    def test_get_gold_price_history(self, api_client):
        """Test getting gold price history."""
        response = api_client.get("/api/v1/gold/history")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


@pytest.mark.integration
class TestStockPriceEndpoints:
    """Tests for stock price endpoints."""

    def test_get_stock_price_history(self, api_client):
        """Test getting stock price history."""
        response = api_client.get("/api/v1/stocks/^GSPC/history")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


@pytest.mark.integration
class TestInflationEndpoints:
    """Tests for inflation rate endpoints."""

    def test_get_inflation_history(self, api_client):
        """Test getting inflation history."""
        response = api_client.get("/api/v1/inflation/USD/history")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_seed_inflation_data(self, api_client):
        """Test seeding inflation data."""
        response = api_client.post("/api/v1/inflation/seed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

