# Finance Assets API

A FastAPI-based application for fetching, storing, and managing historical financial data in MongoDB.

## 🎯 Features

- **Exchange Rates**: USD/PLN, USD/EUR, EUR/PLN (3 years historical data)
- **Inflation Rates**: Monthly data for USD, PLN, and EUR
- **Gold Prices**: Daily gold prices in USD
- **Stock Market**: S&P 500 (US500) daily index data
- **Incremental Updates**: Only fetches new/missing data on subsequent runs
- **Scheduled Jobs**: Automatic daily data updates
- **RESTful API**: FastAPI with automatic documentation
- **MongoDB Storage**: All data stored in MongoDB
- **Comprehensive Logging**: Detailed application and error logging
- **Testing**: Unit and integration tests with pytest

## 📋 Requirements

- Python 3.11+
- MongoDB 4.4+
- Internet connection (for fetching financial data)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd KarTayFinanceAssets

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (MongoDB URI, etc.)
```

### 3. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# Windows (if MongoDB is installed as a service):
net start MongoDB

# Linux/Mac:
sudo systemctl start mongod
# or
brew services start mongodb-community
```

### 4. Run the Application

```bash
# Start the API server
python start_api.py
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

Edit `.env` file to configure the application:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=finance_assets

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Scheduler Configuration
ENABLE_SCHEDULER=True
DAILY_RUN_HOUR=1
DAILY_RUN_MINUTE=0

# Data Configuration
HISTORICAL_YEARS=3

# External API Keys
# Alpha Vantage (stocks, XAUUSD) and FRED (USD/EUR)
ALPHA_VANTAGE_API_KEY=your_api_key_here
FRED_API_KEY=your_fred_api_key_here
```

## 📊 Available Endpoints

### Health & Status
- `GET /api/v1/` - API information
- `GET /api/v1/health` - Health check

### Exchange Rates
- `GET /api/v1/exchange-rates/latest` - Latest rates for all pairs
- `GET /api/v1/exchange-rates/{from}/{to}` - Historical rates for specific pair
- `POST /api/v1/exchange-rates/update` - Manually trigger update (FRED for USD/EUR, NBP for PLN pairs)

### Gold Prices
- `GET /api/v1/gold/latest` - Latest gold price
- `GET /api/v1/gold/history` - Historical gold prices
- `POST /api/v1/gold/update` - Manually trigger update

### Stock Prices (S&P 500)
- `GET /api/v1/stocks/{symbol}/latest` - Latest price for symbol
- `GET /api/v1/stocks/{symbol}/history` - Historical prices
- `POST /api/v1/stocks/sp500/update` - Update S&P 500 data

### Inflation Rates
- `GET /api/v1/inflation/latest/{currency}` - Latest inflation rate
- `GET /api/v1/inflation/{currency}/history` - Historical inflation rates
- `POST /api/v1/inflation/seed` - Seed sample inflation data

### Manual Updates
- `POST /api/v1/update-all` - Trigger update of all data sources

## 🔄 Data Update Strategy

The application implements **incremental data fetching**:

1. **First Run**: Fetches data from the past 3 years (configurable)
2. **Subsequent Runs**: Only fetches data after the latest date in the database
3. **Scheduled Updates**: Runs daily at configured time (default: 1:00 AM)
4. **Manual Updates**: Trigger anytime via API endpoints

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run unit tests only
pytest tests/unit -m unit

# Run integration tests only
pytest tests/integration -m integration

# Run with coverage report
pytest --cov=src --cov=api --cov-report=html
```

## 📁 Project Structure

```
KarTayFinanceAssets/
├── api/                    # API routes and endpoints
│   ├── __init__.py
│   └── routes.py
├── config/                 # Configuration files
│   ├── __init__.py
│   ├── settings.py        # Application settings
│   └── logging_config.py  # Logging configuration
├── src/                   # Source code
│   ├── database/          # Database models and connection
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── models.py
│   ├── services/          # Data fetching services
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── exchange_rate_service.py
│   │   ├── gold_price_service.py
│   │   ├── stock_price_service.py
│   │   └── inflation_service.py
│   └── scheduler/         # Scheduled jobs
│       ├── __init__.py
│       └── data_scheduler.py
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test fixtures
├── logs/                  # Application logs
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Environment template
├── .gitignore
├── pytest.ini            # Pytest configuration
├── .pylintrc             # PyLint configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── start_api.py          # Application entry point
└── README.md             # This file
```

## 🔍 Data Sources

The application uses the following data sources:

- **Exchange Rates**: FRED for USD/EUR ([FRED Daily Rates](https://fred.stlouisfed.org/categories/94)); NBP API for PLN pairs (`https://api.nbp.pl/api/exchangerates/rate`)
- **Gold Prices**: Alpha Vantage (XAU/USD via FX_DAILY)
- **S&P 500**: Alpha Vantage (SPY via TIME_SERIES_DAILY_ADJUSTED)
- **Inflation**: Manual entry (APIs for inflation data typically require paid subscriptions)

## 📝 Logging

Logs are stored in `logs/app.log` with automatic rotation:
- Maximum size: 10MB per file
- Backup count: 5 files
- Console output: INFO level
- File output: DEBUG level

## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
# Windows:
sc query MongoDB

# Linux/Mac:
systemctl status mongod
```

### Import Errors
Make sure you're in the virtual environment:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### No Data Being Fetched
- Check internet connection
- Verify API keys (if using paid services)
- Check logs in `logs/app.log` for errors

## 📄 License

This project is created for educational and personal use.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📞 Support

For issues and questions, please check the logs first:
```bash
tail -f logs/app.log  # Linux/Mac
Get-Content logs/app.log -Wait  # Windows PowerShell
```

## 🗺️ Roadmap

- [ ] Add more currency pairs
- [ ] Implement cryptocurrency data
- [ ] Add data export functionality (CSV, Excel)
- [ ] Create data visualization dashboard
- [ ] Add email notifications for failed updates
- [ ] Implement data validation and cleaning
- [ ] Add support for more stock indices

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [MongoDB](https://www.mongodb.com/) - Database
- [yfinance](https://github.com/ranaroussi/yfinance) - Financial data
- [APScheduler](https://apscheduler.readthedocs.io/) - Job scheduling

