"""Unit tests for provider classes."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.providers.alpha_vantage import AlphaVantageClient
from src.providers.fred import FredClient
from src.providers.nbp import NbpClient
from src.providers.world_bank import WorldBankClient


@pytest.mark.unit
class TestFredClient:
    """Tests for FRED API client."""

    def test_init(self):
        """Test FredClient initialization."""
        client = FredClient()
        assert client is not None

    @patch("src.providers.fred.requests.get")
    def test_fetch_series_daily_success(self, mock_get):
        """Test successful fetch from FRED."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"observations": [{"date": "2024-10-20", "value": "0.92"}]}
        mock_get.return_value = mock_response

        client = FredClient()
        with patch.object(client, "api_key", "test_key"):
            data = client.fetch_series_daily("DEXUSEU", datetime(2024, 10, 1), datetime(2024, 10, 21))

            assert len(data) == 1
            assert data[0]["close"] == 0.92

    @patch("src.providers.fred.requests.get")
    def test_fetch_series_daily_no_api_key(self, mock_get):
        """Test fetch without API key."""
        client = FredClient()
        client.api_key = ""

        data = client.fetch_series_daily("DEXUSEU", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert data == []

    @patch("src.providers.fred.requests.get")
    def test_fetch_series_daily_http_error(self, mock_get):
        """Test fetch with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP error")
        mock_get.return_value = mock_response

        client = FredClient()
        with patch.object(client, "api_key", "test_key"):
            # The client retries 4 times and then raises the exception
            with pytest.raises(Exception, match="HTTP error"):
                client.fetch_series_daily("DEXUSEU", datetime(2024, 10, 1), datetime(2024, 10, 21))


@pytest.mark.unit
class TestNbpClient:
    """Tests for NBP API client."""

    def test_init(self):
        """Test NbpClient initialization."""
        client = NbpClient()
        assert client is not None
        assert client.BASE_URL == "https://api.nbp.pl/api"

    @patch("src.providers.nbp.requests.get")
    def test_fetch_pln_rates_success(self, mock_get):
        """Test successful fetch from NBP."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": [{"effectiveDate": "2024-10-20", "mid": 3.95}]}
        mock_get.return_value = mock_response

        client = NbpClient()
        data = client.fetch_pln_rates("USD", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert len(data) == 1
        assert data[0]["mid"] == 3.95

    @patch("src.providers.nbp.requests.get")
    def test_fetch_pln_rates_error(self, mock_get):
        """Test fetch with error."""
        mock_get.side_effect = Exception("Network error")

        client = NbpClient()
        data = client.fetch_pln_rates("USD", datetime(2024, 10, 1), datetime(2024, 10, 21))

        assert data == []


@pytest.mark.unit
class TestAlphaVantageClient:
    """Tests for Alpha Vantage API client."""

    def test_init(self):
        """Test AlphaVantageClient initialization."""
        client = AlphaVantageClient()
        assert client is not None

    @patch("src.providers.alpha_vantage.requests.get")
    def test_fetch_equity_daily_success(self, mock_get):
        """Test successful fetch equity data from Alpha Vantage."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2024-10-20": {
                    "1. open": "100.0",
                    "2. high": "102.0",
                    "3. low": "99.0",
                    "4. close": "101.0",
                    "5. volume": "1000000",
                }
            }
        }
        mock_get.return_value = mock_response

        client = AlphaVantageClient()
        with patch.object(client, "api_key", "test_key"):
            data = client.fetch_equity_daily("SPY")

            assert len(data) > 0

    @patch("src.providers.alpha_vantage.requests.get")
    def test_fetch_equity_daily_no_api_key(self, mock_get):
        """Test fetch without API key."""
        client = AlphaVantageClient()
        client.api_key = ""

        data = client.fetch_equity_daily("SPY")
        assert data == []

    @patch("src.providers.alpha_vantage.requests.get")
    def test_fetch_fx_daily_success(self, mock_get):
        """Test successful FX fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Time Series FX (Daily)": {
                "2024-10-20": {
                    "1. open": "0.92",
                    "2. high": "0.93",
                    "3. low": "0.91",
                    "4. close": "0.92",
                }
            }
        }
        mock_get.return_value = mock_response

        client = AlphaVantageClient()
        with patch.object(client, "api_key", "test_key"):
            data = client.fetch_fx_daily("USD", "EUR")

            assert len(data) > 0


@pytest.mark.unit
class TestWorldBankClient:
    """Tests for World Bank API client."""

    def test_init(self):
        """Test WorldBankClient initialization."""
        client = WorldBankClient()
        assert client is not None
        assert client.BASE_URL == "https://api.worldbank.org/v2"

    @patch("src.providers.world_bank.requests.get")
    def test_fetch_inflation_cpi_annual_success(self, mock_get):
        """Test successful fetch from World Bank."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {},  # First element is metadata
            [{"date": "2024", "value": 3.2, "country": {"id": "USA"}}],
        ]
        mock_get.return_value = mock_response

        client = WorldBankClient()
        data = client.fetch_inflation_cpi_annual("USA")

        assert len(data) == 1
        assert data[0]["value"] == 3.2

    @patch("src.providers.world_bank.requests.get")
    def test_fetch_inflation_cpi_annual_error(self, mock_get):
        """Test fetch with error."""
        mock_get.side_effect = Exception("Network error")

        client = WorldBankClient()
        data = client.fetch_inflation_cpi_annual("USA")

        assert data == []

    @patch("src.providers.world_bank.requests.get")
    def test_fetch_inflation_cpi_annual_invalid_response(self, mock_get):
        """Test fetch with invalid response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{}]  # Missing data
        mock_get.return_value = mock_response

        client = WorldBankClient()
        data = client.fetch_inflation_cpi_annual("USA")

        assert data == []
