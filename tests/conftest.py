"""Pytest configuration and fixtures."""
import pytest
from datetime import datetime
from mongomock import MongoClient
from fastapi.testclient import TestClient
from pymongo.database import Database


@pytest.fixture
def mock_db():
    """Create a mock MongoDB database for testing."""
    client = MongoClient()
    db = client["test_finance_assets"]
    yield db
    client.close()


@pytest.fixture
def sample_exchange_rate():
    """Sample exchange rate data."""
    return {
        "date": datetime(2024, 10, 20),
        "from_currency": "USD",
        "to_currency": "PLN",
        "rate": 3.95,
        "source": "test",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def sample_gold_price():
    """Sample gold price data."""
    return {
        "date": datetime(2024, 10, 20),
        "price_usd": 1975.50,
        "source": "test",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def sample_stock_price():
    """Sample stock price data."""
    return {
        "date": datetime(2024, 10, 20),
        "symbol": "^GSPC",
        "open_price": 4500.00,
        "high_price": 4520.00,
        "low_price": 4490.00,
        "close_price": 4510.00,
        "volume": 1000000.0,
        "source": "test",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def sample_inflation_rate():
    """Sample inflation rate data."""
    return {
        "date": datetime(2024, 10, 1),
        "currency": "USD",
        "rate": 3.2,
        "source": "test",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def api_client():
    """Create a test client for the API."""
    from start_api import app
    from src.database import get_database
    
    # Override database dependency with mock
    def override_get_database():
        client = MongoClient()
        return client["test_finance_assets"]
    
    app.dependency_overrides[get_database] = override_get_database
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

