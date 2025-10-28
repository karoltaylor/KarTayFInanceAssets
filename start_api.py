"""Main application entry point for Finance Assets API."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from config.logging_config import setup_logging, get_logger
from src.database import get_database, close_database_connection
from src.scheduler import DataScheduler
from api.routes import router


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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

