"""Scheduler for automated daily data updates."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pymongo.database import Database
from config import settings
from config.logging_config import get_logger
from src.services import (
    ExchangeRateService,
    GoldPriceService,
    StockPriceService
)


class DataScheduler:
    """Scheduler for automated data fetching."""

    def __init__(self, db: Database):
        """
        Initialize the data scheduler.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.logger = get_logger(__name__)
        self.scheduler = BackgroundScheduler()
        self.services = {
            "exchange_rates": ExchangeRateService(db),
            "gold_prices": GoldPriceService(db),
            "stock_prices": StockPriceService(db)
        }

    def update_all_data(self):
        """Update all financial data sources."""
        self.logger.info("=== Starting scheduled data update ===")
        
        try:
            # Update exchange rates
            self.logger.info("Updating exchange rates...")
            ex_stats = self.services["exchange_rates"].update_all_pairs()
            self.logger.info(f"Exchange rates update: {ex_stats}")

            # Update gold prices
            self.logger.info("Updating gold prices...")
            gold_stats = self.services["gold_prices"].update_gold_prices()
            self.logger.info(f"Gold prices update: {gold_stats}")

            # Update S&P 500
            self.logger.info("Updating S&P 500...")
            sp500_stats = self.services["stock_prices"].update_sp500()
            self.logger.info(f"S&P 500 update: {sp500_stats}")

            self.logger.info("=== Scheduled data update completed successfully ===")
            
        except Exception as e:
            self.logger.error(f"Error during scheduled update: {str(e)}")

    def start(self):
        """Start the scheduler."""
        if not settings.enable_scheduler:
            self.logger.info("Scheduler is disabled in settings")
            return

        # Schedule daily data update
        trigger = CronTrigger(
            hour=settings.daily_run_hour,
            minute=settings.daily_run_minute
        )
        
        self.scheduler.add_job(
            self.update_all_data,
            trigger=trigger,
            id="daily_data_update",
            name="Daily financial data update",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.logger.info(
            f"Scheduler started. Daily updates at {settings.daily_run_hour:02d}:{settings.daily_run_minute:02d}"
        )

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")

    def run_now(self):
        """Manually trigger a data update immediately."""
        self.logger.info("Manual data update triggered")
        self.update_all_data()

