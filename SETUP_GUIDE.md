# Setup Guide - Finance Assets API

This guide will walk you through setting up the Finance Assets API from scratch.

## Prerequisites

### 1. Install Python 3.11+

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS:**
```bash
brew install python@3.11
```

### 2. Install MongoDB

**Windows:**
- Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
- Install as a Windows Service

**Linux (Ubuntu/Debian):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

## Step-by-Step Setup

### 1. Create Project Directory

```bash
# Navigate to your projects folder
cd C:\Users\karol\projects  # Windows
cd ~/projects              # Linux/Mac

# The project should already exist as KarTayFinanceAssets
cd KarTayFinanceAssets
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows Command Prompt:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Verify activation (should show path to venv)
which python  # Linux/Mac
where python  # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy environment template
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Edit `.env` file with your settings:

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
# Sign up at https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 5. Create Logs Directory

```bash
# Windows:
mkdir logs
# Linux/Mac:
mkdir -p logs
```

### 6. Verify MongoDB Connection

```bash
# Test MongoDB connection
# Windows:
mongo --eval "db.runCommand({ connectionStatus: 1 })"
# Or using mongosh (newer versions):
mongosh --eval "db.runCommand({ connectionStatus: 1 })"

# Linux/Mac:
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

### 7. Run Tests (Optional)

```bash
# Run all tests to verify setup
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest tests/unit -m unit
pytest tests/integration -m integration
```

### 8. Start the Application

```bash
# Start the API server
python start_api.py
```

You should see output like:
```
2024-10-20 10:00:00 - finance_assets - INFO - ============================================================
2024-10-20 10:00:00 - finance_assets - INFO - Starting Finance Assets API
2024-10-20 10:00:00 - finance_assets - INFO - ============================================================
2024-10-20 10:00:00 - finance_assets - INFO - Connecting to MongoDB at mongodb://localhost:27017
2024-10-20 10:00:00 - finance_assets - INFO - Successfully connected to database: finance_assets
2024-10-20 10:00:00 - finance_assets - INFO - Scheduler started. Daily updates at 01:00
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 9. Verify Installation

Open your browser and navigate to:

1. **API Documentation**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/api/v1/health
3. **API Info**: http://localhost:8000/api/v1/

### 10. Trigger Initial Data Load

You can manually trigger the initial data fetch:

```bash
# Using curl (Linux/Mac):
curl -X POST http://localhost:8000/api/v1/update-all

# Using PowerShell (Windows):
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/update-all

# Or use the interactive API docs:
# Go to http://localhost:8000/docs
# Find "POST /api/v1/update-all"
# Click "Try it out" → "Execute"
```

This will fetch:
- 3 years of exchange rate data (USD/PLN, USD/EUR, EUR/PLN)
- 3 years of gold prices
- 3 years of S&P 500 data

**Note**: The initial data fetch may take 2-5 minutes depending on your internet connection.

## Verification Checklist

- [ ] Python 3.11+ installed and accessible
- [ ] MongoDB installed and running
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] `.env` file created and configured
- [ ] MongoDB connection successful
- [ ] Tests pass (optional but recommended)
- [ ] API server starts without errors
- [ ] Can access API documentation at http://localhost:8000/docs
- [ ] Health check returns "healthy" status
- [ ] Initial data load completes successfully

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: MongoDB Connection Failed

**Solution**: Verify MongoDB is running
```bash
# Windows:
sc query MongoDB
# If not running:
net start MongoDB

# Linux/Mac:
systemctl status mongod
# If not running:
sudo systemctl start mongod
```

### Issue: Port 8000 Already in Use

**Solution**: Change port in `.env` file
```env
API_PORT=8001  # Or any other available port
```

### Issue: Permission Denied (Linux/Mac)

**Solution**: Create logs directory with proper permissions
```bash
mkdir -p logs
chmod 755 logs
```

### Issue: yfinance Data Download Errors

**Solution**: This is usually temporary. Try:
1. Check internet connection
2. Wait a few minutes and try again
3. Check Yahoo Finance website to ensure it's accessible

## Next Steps

After successful setup:

1. **Explore the API**: Use the interactive docs at http://localhost:8000/docs
2. **Schedule Regular Updates**: The scheduler will run daily at the configured time
3. **Monitor Logs**: Check `logs/app.log` for application events
4. **Query Data**: Use the API endpoints to retrieve financial data
5. **Customize**: Modify configuration in `.env` as needed

## Development Workflow

For development work:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Make code changes

# 3. Run tests
pytest

# 4. Check code quality
pylint api/ src/

# 5. Run the application
python start_api.py
```

## Production Deployment

For production deployment, consider:

1. **Use Production MongoDB**: Configure `MONGODB_URI` to point to production database
2. **Disable Reload**: Set `API_RELOAD=False` in `.env`
3. **Use Process Manager**: Use systemd, supervisor, or PM2 to manage the process
4. **Reverse Proxy**: Use nginx or Apache as a reverse proxy
5. **HTTPS**: Configure SSL/TLS certificates
6. **Environment Variables**: Use secure secret management
7. **Monitoring**: Set up application monitoring and alerting

## Support

If you encounter issues:

1. Check the logs: `logs/app.log`
2. Verify all prerequisites are installed
3. Ensure MongoDB is running
4. Check the troubleshooting section in README.md
5. Review error messages carefully

Happy coding! 🚀

