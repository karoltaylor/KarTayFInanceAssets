# Quick Reference Guide

## 📦 Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# 4. Ensure MongoDB is running
```

## 🚀 Starting the Application

```bash
# Start API server
python start_api.py

# Quick start with data check
python quick_start.py
```

## 🔗 Key URLs

- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health
- **ReDoc**: http://localhost:8000/redoc

## 📋 Common Commands

### Testing
```bash
pytest                      # Run all tests
pytest tests/unit          # Unit tests only
pytest tests/integration   # Integration tests
pytest -v                  # Verbose output
pytest --cov               # With coverage
```

### Code Quality
```bash
pylint api/ src/           # Lint code
black api/ src/ tests/     # Format code
```

### Data Management
```bash
# Fetch/update all data
curl -X POST http://localhost:8000/api/v1/update-all

# Update specific data types
curl -X POST http://localhost:8000/api/v1/exchange-rates/update
curl -X POST http://localhost:8000/api/v1/gold/update
curl -X POST http://localhost:8000/api/v1/stocks/sp500/update
```

## 🗂️ Project Structure

```
KarTayFinanceAssets/
├── api/                   # API routes
├── config/                # Configuration
├── src/
│   ├── database/         # Models & connection
│   ├── services/         # Data fetching
│   └── scheduler/        # Scheduled jobs
├── tests/                # Test suite
├── logs/                 # Application logs
└── start_api.py          # Main entry point
```

## 📊 Data Types

| Data Type | Collection | Update Frequency |
|-----------|-----------|------------------|
| Exchange Rates | `exchange_rates` | Daily |
| Gold Prices | `gold_prices` | Daily |
| S&P 500 | `stock_prices` | Daily |
| Inflation | `inflation_rates` | Manual |

## 🔧 Configuration (.env)

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=finance_assets

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
ENABLE_SCHEDULER=True
DAILY_RUN_HOUR=1
DAILY_RUN_MINUTE=0

# Data
HISTORICAL_YEARS=3
```

## 📡 API Endpoints

### Exchange Rates
- `GET /api/v1/exchange-rates/latest`
- `GET /api/v1/exchange-rates/{from}/{to}`
- `POST /api/v1/exchange-rates/update`

### Gold
- `GET /api/v1/gold/latest`
- `GET /api/v1/gold/history`
- `POST /api/v1/gold/update`

### Stocks
- `GET /api/v1/stocks/{symbol}/latest`
- `GET /api/v1/stocks/{symbol}/history`
- `POST /api/v1/stocks/sp500/update`

### Inflation
- `GET /api/v1/inflation/latest/{currency}`
- `GET /api/v1/inflation/{currency}/history`
- `POST /api/v1/inflation/seed`

## 🐛 Troubleshooting

### MongoDB not connecting
```bash
# Check status
sc query MongoDB  # Windows
systemctl status mongod  # Linux

# Start service
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

### Import errors
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Port already in use
Change `API_PORT` in `.env` file

### Check logs
```bash
# View logs
cat logs/app.log  # Linux/Mac
type logs\app.log  # Windows
```

## 📚 Documentation

- **README.md**: Comprehensive documentation
- **SETUP_GUIDE.md**: Step-by-step setup
- **API_USAGE_EXAMPLES.md**: API usage examples
- **QUICK_REFERENCE.md**: This file

## 💡 Quick Tips

1. **First time setup**: Run `python quick_start.py`
2. **Manual data fetch**: Use POST `/api/v1/update-all`
3. **View logs**: Check `logs/app.log` for issues
4. **Test API**: Use http://localhost:8000/docs
5. **Incremental updates**: Data fetches only new records

## 🔄 Daily Workflow

```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Start API
python start_api.py

# 3. Scheduler runs automatically at configured time

# 4. Or manually trigger update
curl -X POST http://localhost:8000/api/v1/update-all
```

## 📞 Support

1. Check logs: `logs/app.log`
2. Review documentation
3. Test MongoDB connection
4. Verify environment variables
5. Check internet connectivity

