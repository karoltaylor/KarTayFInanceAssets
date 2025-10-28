"""API routes for the Finance Assets API."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.database import Database

from config.logging_config import get_logger
from src.database import get_database
from src.services import (
    ExchangeRateService,
    GoldPriceService,
    InflationService,
    StockPriceService,
)

router = APIRouter()
logger = get_logger(__name__)


# Dependency to get database
def get_db():
    """Get database instance."""
    return get_database()


@router.get("/")
async def root():
    """Root endpoint."""
    return {"name": "Finance Assets API", "version": "1.0.0", "description": "API for historical financial data"}


@router.get("/health")
async def health_check(db: Database = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.client.admin.command("ping")
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}") from e


# Exchange Rate Endpoints
@router.get("/exchange-rates/latest")
async def get_latest_exchange_rates(db: Database = Depends(get_db)):
    """Get the latest exchange rates for all currency pairs."""
    service = ExchangeRateService(db)
    rates = service.get_latest_rates()
    return {"data": rates, "count": len(rates)}


@router.get("/exchange-rates/{from_currency}/{to_currency}")
async def get_exchange_rate_history(
    from_currency: str,
    to_currency: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_db),
):
    """Get exchange rate history for a specific currency pair."""
    service = ExchangeRateService(db)

    query = {"from_currency": from_currency.upper(), "to_currency": to_currency.upper()}

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)

    rates = list(service.collection.find(query).sort("date", -1).limit(limit))
    return {"data": rates, "count": len(rates)}


@router.post("/exchange-rates/update")
async def update_exchange_rates(db: Database = Depends(get_db)):
    """Manually trigger an update of all exchange rates."""
    service = ExchangeRateService(db)
    stats = service.update_all_pairs()
    return {"status": "success", "stats": stats}


# Gold Price Endpoints
@router.get("/gold/latest")
async def get_latest_gold_price(db: Database = Depends(get_db)):
    """Get the latest gold price."""
    service = GoldPriceService(db)
    price = service.get_latest_price()

    if not price:
        raise HTTPException(status_code=404, detail="No gold price data available")

    return {"data": price}


@router.get("/gold/history")
async def get_gold_price_history(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_db),
):
    """Get gold price history."""
    service = GoldPriceService(db)

    query = {}
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)

    prices = list(service.collection.find(query).sort("date", -1).limit(limit))
    return {"data": prices, "count": len(prices)}


@router.post("/gold/update")
async def update_gold_prices(db: Database = Depends(get_db)):
    """Manually trigger an update of gold prices."""
    service = GoldPriceService(db)
    stats = service.update_gold_prices()
    return {"status": "success", "stats": stats}


# Stock Price Endpoints (S&P 500)
@router.get("/stocks/{symbol}/latest")
async def get_latest_stock_price(symbol: str, db: Database = Depends(get_db)):
    """Get the latest price for a stock/index."""
    service = StockPriceService(db)
    price = service.get_latest_price(symbol.upper())

    if not price:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    return {"data": price}


@router.get("/stocks/{symbol}/history")
async def get_stock_price_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_db),
):
    """Get price history for a stock/index."""
    service = StockPriceService(db)

    query = {"symbol": symbol.upper()}
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)

    prices = list(service.collection.find(query).sort("date", -1).limit(limit))
    return {"data": prices, "count": len(prices)}


@router.post("/stocks/sp500/update")
async def update_sp500_prices(db: Database = Depends(get_db)):
    """Manually trigger an update of S&P 500 index data."""
    service = StockPriceService(db)
    stats = service.update_sp500()
    return {"status": "success", "stats": stats}


# Inflation Rate Endpoints
@router.get("/inflation/latest/{currency}")
async def get_latest_inflation_rate(currency: str, db: Database = Depends(get_db)):
    """Get the latest inflation rate for a currency."""
    service = InflationService(db)
    rate = service.get_latest_rate(currency.upper())

    if not rate:
        raise HTTPException(status_code=404, detail=f"No inflation data available for {currency}")

    return {"data": rate}


@router.get("/inflation/{currency}/history")
async def get_inflation_history(
    currency: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Database = Depends(get_db),
):
    """Get inflation rate history for a currency."""
    service = InflationService(db)

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    rates = service.get_rates_by_currency(currency.upper(), start, end)
    return {"data": rates, "count": len(rates)}


@router.post("/inflation/seed")
async def seed_inflation_data(db: Database = Depends(get_db)):
    """Seed sample inflation data (for testing purposes)."""
    service = InflationService(db)
    count = service.seed_sample_data()
    return {"status": "success", "inserted": count}


@router.post("/inflation/update-worldbank")
async def update_inflation_worldbank(db: Database = Depends(get_db)):
    """Fetch and store inflation data from World Bank for USA, POL, DEU, EUU."""
    service = InflationService(db)
    stats = service.update_inflation_from_world_bank()
    return {"status": "success", "stats": stats}


# Manual Update All Data
@router.post("/update-all")
async def update_all_data(db: Database = Depends(get_db)):
    """Manually trigger an update of all financial data."""
    from src.scheduler import DataScheduler

    try:
        logger.info("Manual data update requested via /update-all")
        scheduler = DataScheduler(db)
        scheduler.run_now()
        logger.info("Manual data update completed")
        return {"status": "success", "message": "Data update triggered"}
    except Exception as e:
        logger.exception(f"Manual data update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Data update failed; see logs for details") from e
