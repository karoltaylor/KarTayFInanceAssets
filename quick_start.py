"""
Quick start script to verify setup and fetch initial data.

This script:
1. Checks MongoDB connection
2. Displays current data statistics
3. Optionally fetches initial data
4. Shows sample data from each collection
"""

import sys
from datetime import datetime
from config import settings
from config.logging_config import setup_logging, get_logger
from src.database import get_database, close_database_connection
from src.services import (
    ExchangeRateService,
    GoldPriceService,
    StockPriceService,
    InflationService
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


def check_mongodb_connection():
    """Check if MongoDB is accessible."""
    try:
        db = get_database()
        db.client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {str(e)}")
        return False


def get_collection_stats(db):
    """Get statistics for all collections."""
    collections = {
        "exchange_rates": ExchangeRateService,
        "gold_prices": GoldPriceService,
        "stock_prices": StockPriceService,
        "inflation_rates": InflationService
    }
    
    stats = {}
    for name, service_class in collections.items():
        service = service_class(db)
        count = service.collection.count_documents({})
        stats[name] = count
    
    return stats


def display_stats(stats):
    """Display collection statistics."""
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    for collection, count in stats.items():
        print(f"{collection:20s}: {count:>8,d} records")
    
    total = sum(stats.values())
    print("-" * 60)
    print(f"{'TOTAL':20s}: {total:>8,d} records")
    print("=" * 60 + "\n")


def show_sample_data(db):
    """Show sample data from each collection."""
    print("\n" + "=" * 60)
    print("SAMPLE DATA")
    print("=" * 60)
    
    # Exchange Rates
    ex_service = ExchangeRateService(db)
    latest_rates = ex_service.get_latest_rates()
    if latest_rates:
        print("\nLatest Exchange Rates:")
        for rate in latest_rates:
            print(f"  {rate['from_currency']}/{rate['to_currency']}: {rate['rate']:.4f} ({rate['date'].date()})")
    else:
        print("\nExchange Rates: No data available")
    
    # Gold Prices
    gold_service = GoldPriceService(db)
    latest_gold = gold_service.get_latest_price()
    if latest_gold:
        print(f"\nLatest Gold Price:")
        print(f"  ${latest_gold['price_usd']:.2f} per ounce ({latest_gold['date'].date()})")
    else:
        print("\nGold Prices: No data available")
    
    # S&P 500
    stock_service = StockPriceService(db)
    latest_sp500 = stock_service.get_latest_price("^GSPC")
    if latest_sp500:
        print(f"\nLatest S&P 500:")
        print(f"  Close: {latest_sp500['close_price']:.2f} ({latest_sp500['date'].date()})")
    else:
        print("\nS&P 500: No data available")
    
    # Inflation
    inflation_service = InflationService(db)
    for currency in ["USD", "EUR", "PLN"]:
        latest_inflation = inflation_service.get_latest_rate(currency)
        if latest_inflation:
            print(f"\nLatest {currency} Inflation:")
            print(f"  {latest_inflation['rate']:.2f}% ({latest_inflation['date'].date()})")
    
    print("\n" + "=" * 60 + "\n")


def fetch_initial_data(db):
    """Fetch initial data for all sources."""
    print("\n" + "=" * 60)
    print("FETCHING INITIAL DATA")
    print("=" * 60)
    print("\nThis may take 2-5 minutes depending on your internet connection...")
    print("Please wait...\n")
    
    try:
        # Exchange Rates
        print("Fetching exchange rates...")
        ex_service = ExchangeRateService(db)
        ex_stats = ex_service.update_all_pairs()
        print(f"  ✓ Inserted {ex_stats['total_inserted']} exchange rate records")
        
        # Gold Prices
        print("\nFetching gold prices...")
        gold_service = GoldPriceService(db)
        gold_stats = gold_service.update_gold_prices()
        print(f"  ✓ Inserted {gold_stats['total_inserted']} gold price records")
        
        # S&P 500
        print("\nFetching S&P 500 data...")
        stock_service = StockPriceService(db)
        stock_stats = stock_service.update_sp500()
        print(f"  ✓ Inserted {stock_stats['total_inserted']} S&P 500 records")
        
        # Inflation (seed sample data)
        print("\nSeeding sample inflation data...")
        inflation_service = InflationService(db)
        inflation_count = inflation_service.seed_sample_data()
        print(f"  ✓ Inserted {inflation_count} inflation rate records")
        
        print("\n" + "=" * 60)
        print("DATA FETCH COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        print(f"\n✗ Error occurred: {str(e)}\n")
        return False


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("FINANCE ASSETS API - QUICK START")
    print("=" * 60)
    print(f"\nMongoDB URI: {settings.mongodb_uri}")
    print(f"Database: {settings.mongodb_database}")
    print(f"Historical Years: {settings.historical_years}")
    print()
    
    # Check MongoDB connection
    if not check_mongodb_connection():
        print("\nPlease ensure MongoDB is running and accessible.")
        print("See SETUP_GUIDE.md for installation instructions.\n")
        sys.exit(1)
    
    try:
        db = get_database()
        
        # Get and display current stats
        stats = get_collection_stats(db)
        display_stats(stats)
        
        # If no data, offer to fetch
        if sum(stats.values()) == 0:
            print("No data found in database.")
            response = input("\nWould you like to fetch initial data? (y/n): ")
            
            if response.lower() in ['y', 'yes']:
                if fetch_initial_data(db):
                    # Show updated stats and sample data
                    stats = get_collection_stats(db)
                    display_stats(stats)
                    show_sample_data(db)
            else:
                print("\nYou can fetch data later by:")
                print("  1. Running this script again")
                print("  2. Starting the API and calling POST /api/v1/update-all")
                print("  3. Waiting for the scheduled daily update\n")
        else:
            # Show sample data
            show_sample_data(db)
            
            # Offer to update
            response = input("\nWould you like to update with latest data? (y/n): ")
            if response.lower() in ['y', 'yes']:
                fetch_initial_data(db)
                stats = get_collection_stats(db)
                display_stats(stats)
                show_sample_data(db)
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\n1. Start the API server:")
        print("   python start_api.py")
        print("\n2. Access API documentation:")
        print("   http://localhost:8000/docs")
        print("\n3. Check API health:")
        print("   http://localhost:8000/api/v1/health")
        print("\n4. View usage examples:")
        print("   See API_USAGE_EXAMPLES.md")
        print("\n" + "=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\n✗ An error occurred: {str(e)}\n")
        sys.exit(1)
    finally:
        close_database_connection()


if __name__ == "__main__":
    main()

