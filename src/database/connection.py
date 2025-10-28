"""MongoDB database connection management."""

from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from config import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_database() -> Database:
    """
    Get MongoDB database instance with connection pooling.

    Returns:
        Database: MongoDB database instance

    Raises:
        ConnectionError: If unable to connect to MongoDB
    """
    global _client, _database

    if _database is None:
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_uri}")
            _client = MongoClient(
                settings.mongodb_uri,
                maxPoolSize=settings.mongodb_max_pool_size,
                minPoolSize=settings.mongodb_min_pool_size,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True,
                retryReads=True,
            )
            _database = _client[settings.mongodb_database]

            # Test connection
            _client.admin.command("ping")
            logger.info(
                f"Successfully connected to database: {settings.mongodb_database} "
                f"(pool: {settings.mongodb_min_pool_size}-{settings.mongodb_max_pool_size})"
            )

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(f"Unable to connect to MongoDB: {str(e)}") from e

    return _database


def close_database_connection():
    """Close MongoDB database connection."""
    global _client, _database

    if _client:
        logger.info("Closing MongoDB connection")
        _client.close()
        _client = None
        _database = None
