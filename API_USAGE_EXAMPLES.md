# API Usage Examples

This document provides practical examples of using the Finance Assets API.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. Configure your Alpha Vantage API key in `.env` as `ALPHA_VANTAGE_API_KEY`.

## Examples

### 1. Check API Health

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-10-20T10:00:00.000000"
}
```

### 2. Get Latest Exchange Rates

**Request:**
```bash
curl http://localhost:8000/api/v1/exchange-rates/latest
```

**Response:**
```json
{
  "data": [
    {
      "_id": "...",
      "date": "2024-10-20T00:00:00",
      "from_currency": "USD",
      "to_currency": "PLN",
      "rate": 3.95,
      "source": "yfinance",
      "created_at": "2024-10-20T10:00:00"
    },
    {
      "_id": "...",
      "date": "2024-10-20T00:00:00",
      "from_currency": "USD",
      "to_currency": "EUR",
      "rate": 0.92,
      "source": "yfinance",
      "created_at": "2024-10-20T10:00:00"
    }
  ],
  "count": 3
}
```

### 3. Get Exchange Rate History for Specific Pair

**Request:**
```bash
# Get last 30 days of USD/PLN
curl "http://localhost:8000/api/v1/exchange-rates/USD/PLN?limit=30"

# Get specific date range
curl "http://localhost:8000/api/v1/exchange-rates/USD/PLN?start_date=2024-01-01&end_date=2024-03-31&limit=100"
```

**Response:**
```json
{
  "data": [
    {
      "_id": "...",
      "date": "2024-10-20T00:00:00",
      "from_currency": "USD",
      "to_currency": "PLN",
      "rate": 3.95,
      "source": "yfinance",
      "created_at": "2024-10-20T10:00:00"
    }
  ],
  "count": 1
}
```

### 4. Get Latest Gold Price

**Request:**
```bash
curl http://localhost:8000/api/v1/gold/latest
```

**Response:**
```json
{
  "data": {
    "_id": "...",
    "date": "2024-10-20T00:00:00",
    "price_usd": 1975.50,
    "source": "yfinance",
    "created_at": "2024-10-20T10:00:00"
  }
}
```

### 5. Get Gold Price History

**Request:**
```bash
# Get last 90 days
curl "http://localhost:8000/api/v1/gold/history?limit=90"

# Get specific date range
curl "http://localhost:8000/api/v1/gold/history?start_date=2024-01-01&end_date=2024-10-20"
```

### 6. Get Latest S&P 500 Price

**Request:**
```bash
curl http://localhost:8000/api/v1/stocks/^GSPC/latest
```

**Response:**
```json
{
  "data": {
    "_id": "...",
    "date": "2024-10-20T00:00:00",
    "symbol": "^GSPC",
    "open_price": 4500.00,
    "high_price": 4520.00,
    "low_price": 4490.00,
    "close_price": 4510.00,
    "volume": 1000000.0,
    "source": "yfinance",
    "created_at": "2024-10-20T10:00:00"
  }
}
```

### 7. Get Stock Price History

**Request:**
```bash
# Get last 100 days of S&P 500
curl "http://localhost:8000/api/v1/stocks/^GSPC/history?limit=100"

# Get specific date range
curl "http://localhost:8000/api/v1/stocks/^GSPC/history?start_date=2024-01-01&end_date=2024-12-31"
```

### 8. Get Latest Inflation Rate

**Request:**
```bash
curl http://localhost:8000/api/v1/inflation/latest/USD
```

**Response:**
```json
{
  "data": {
    "_id": "...",
    "date": "2024-10-01T00:00:00",
    "currency": "USD",
    "rate": 3.2,
    "source": "manual",
    "created_at": "2024-10-20T10:00:00"
  }
}
```

### 9. Get Inflation History

**Request:**
```bash
# Get all inflation data for USD
curl http://localhost:8000/api/v1/inflation/USD/history

# Get specific date range
curl "http://localhost:8000/api/v1/inflation/USD/history?start_date=2024-01-01&end_date=2024-12-31"
```

### 10. Manually Update All Data

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/update-all
```

**Response:**
```json
{
  "status": "success",
  "message": "Data update triggered"
}
```

### 11. Update Specific Data Types

**Exchange Rates:**
```bash
curl -X POST http://localhost:8000/api/v1/exchange-rates/update
```

**Gold Prices:**
```bash
curl -X POST http://localhost:8000/api/v1/gold/update
```

**S&P 500:**
```bash
curl -X POST http://localhost:8000/api/v1/stocks/sp500/update
```

**Seed Inflation Data (sample):**
```bash
curl -X POST http://localhost:8000/api/v1/inflation/seed
```

## Python Examples

### Using `requests` Library

```python
import requests

# Base URL
base_url = "http://localhost:8000/api/v1"

# Get latest exchange rates
response = requests.get(f"{base_url}/exchange-rates/latest")
data = response.json()
print(f"Found {data['count']} exchange rates")

# Get USD/PLN history
response = requests.get(
    f"{base_url}/exchange-rates/USD/PLN",
    params={"limit": 30}
)
rates = response.json()["data"]
for rate in rates:
    print(f"{rate['date']}: {rate['rate']}")

# Get latest gold price
response = requests.get(f"{base_url}/gold/latest")
gold = response.json()["data"]
print(f"Gold: ${gold['price_usd']:.2f}")

# Trigger data update
response = requests.post(f"{base_url}/update-all")
print(response.json())
```

### Using `httpx` Library (Async)

```python
import httpx
import asyncio

async def fetch_data():
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        # Get multiple endpoints concurrently
        tasks = [
            client.get(f"{base_url}/exchange-rates/latest"),
            client.get(f"{base_url}/gold/latest"),
            client.get(f"{base_url}/stocks/^GSPC/latest"),
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            print(response.json())

# Run async function
asyncio.run(fetch_data())
```

## PowerShell Examples

### Get Data
```powershell
# Get latest exchange rates
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/exchange-rates/latest"

# Get gold price history
$params = @{
    start_date = "2024-01-01"
    end_date = "2024-10-20"
    limit = 100
}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/gold/history" -Body $params
```

### Trigger Updates
```powershell
# Update all data
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/update-all"

# Update exchange rates only
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/exchange-rates/update"
```

## JavaScript/Node.js Examples

### Using `fetch` API

```javascript
// Get latest exchange rates
async function getExchangeRates() {
    const response = await fetch('http://localhost:8000/api/v1/exchange-rates/latest');
    const data = await response.json();
    console.log(`Found ${data.count} exchange rates`);
    return data.data;
}

// Get gold price history
async function getGoldHistory(startDate, endDate) {
    const url = new URL('http://localhost:8000/api/v1/gold/history');
    url.searchParams.append('start_date', startDate);
    url.searchParams.append('end_date', endDate);
    
    const response = await fetch(url);
    const data = await response.json();
    return data.data;
}

// Trigger data update
async function updateAllData() {
    const response = await fetch('http://localhost:8000/api/v1/update-all', {
        method: 'POST'
    });
    const result = await response.json();
    console.log(result.message);
}

// Usage
getExchangeRates().then(rates => console.log(rates));
getGoldHistory('2024-01-01', '2024-10-20').then(prices => console.log(prices));
updateAllData();
```

## Query Parameters

### Common Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start_date` | string | Start date (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | string | End date (YYYY-MM-DD) | `2024-12-31` |
| `limit` | integer | Max records to return (1-1000) | `100` |

## Response Formats

All successful responses return JSON with this structure:

```json
{
  "data": [...],  // Single object or array
  "count": 123    // Number of records (for list endpoints)
}
```

Error responses:

```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting using:
- FastAPI middleware
- Redis-based rate limiting
- API Gateway

## Best Practices

1. **Use Query Parameters**: Limit result sets with `limit` and date ranges
2. **Handle Errors**: Always check response status codes
3. **Cache Results**: Consider caching frequently accessed data
4. **Batch Requests**: Use the `/update-all` endpoint instead of updating each source separately
5. **Monitor Logs**: Check `logs/app.log` for API usage and errors

## Interactive API Documentation

For interactive testing and exploration:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Try out all endpoints
- See request/response schemas
- View example data
- Test with different parameters

