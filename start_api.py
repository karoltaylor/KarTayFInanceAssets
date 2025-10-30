"""Main application entry point for Finance Assets API."""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import settings
from config.logging_config import get_logger, setup_logging
from src.database import close_database_connection, get_database
from src.scheduler import DataScheduler


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Finance Assets API")
    logger.info("=" * 60)
    
    try:
        # Initialize database connection
        db = get_database()
        logger.info("Database connection established")
        
        # Start scheduler
        global scheduler
        scheduler = DataScheduler(db)
        scheduler.start()
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Finance Assets API")
    
    if scheduler:
        scheduler.stop()
    
    close_database_connection()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Finance Assets API",
    description="API for fetching and storing historical financial data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["finance"])


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "start_api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )

