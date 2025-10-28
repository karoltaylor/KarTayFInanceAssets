"""Base service class for data fetching services."""
from datetime import datetime, timedelta
from typing import Optional
from pymongo.database import Database
from config import settings
from config.logging_config import get_logger


class BaseDataService:
    """Base class for data fetching services."""

    def __init__(self, db: Database, collection_name: str):
        """
        Initialize base service.
        
        Args:
            db: MongoDB database instance
            collection_name: Name of the collection to use
        """
        self.db = db
        self.collection = db[collection_name]
        self.logger = get_logger(self.__class__.__name__)

    def get_latest_date(self, query_filter: Optional[dict] = None) -> Optional[datetime]:
        """
        Get the latest date in the collection.
        
        Args:
            query_filter: Optional filter for the query
            
        Returns:
            Latest date or None if collection is empty
        """
        filter_dict = query_filter or {}
        latest = self.collection.find_one(
            filter_dict,
            sort=[("date", -1)]
        )
        return latest["date"] if latest else None

    def get_start_date(self, query_filter: Optional[dict] = None) -> datetime:
        """
        Get the start date for data fetching.
        
        If data exists, returns the day after the latest date.
        Otherwise, returns date from HISTORICAL_YEARS ago.
        
        Args:
            query_filter: Optional filter for the query
            
        Returns:
            Start date for data fetching
        """
        latest_date = self.get_latest_date(query_filter)
        
        if latest_date:
            # Start from the next day after latest date
            start_date = latest_date + timedelta(days=1)
            self.logger.info(f"Found existing data. Starting from {start_date.date()}")
        else:
            # Start from HISTORICAL_YEARS ago
            start_date = datetime.now() - timedelta(days=365 * settings.historical_years)
            self.logger.info(f"No existing data. Starting from {start_date.date()}")
        
        return start_date

    def bulk_insert(self, records: list):
        """
        Bulk insert records into the collection.
        
        Args:
            records: List of records to insert
            
        Returns:
            Number of inserted records
        """
        if not records:
            self.logger.info("No new records to insert")
            return 0
        
        try:
            result = self.collection.insert_many(records, ordered=False)
            count = len(result.inserted_ids)
            self.logger.info(f"Successfully inserted {count} records")
            return count
        except Exception as e:
            self.logger.error(f"Error inserting records: {str(e)}")
            raise

    def create_indexes(self, indexes: list):
        """
        Create indexes on the collection.
        
        Args:
            indexes: List of index specifications
        """
        try:
            for index in indexes:
                self.collection.create_index(index, unique=True)
            self.logger.info(f"Created indexes on collection {self.collection.name}")
        except Exception as e:
            self.logger.warning(f"Error creating indexes: {str(e)}")

