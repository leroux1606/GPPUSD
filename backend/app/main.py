"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.config import settings
from app.core.database import init_db, check_db_connection
from app.utils.logger import logger
from app.api.routes import data, strategies, backtesting, trading, analytics, indicators
from app.api.websocket import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting GBP/USD Trading Application...")
    
    # Initialize database
    try:
        init_db()
        if check_db_connection():
            logger.info("Database connection established")
        else:
            logger.warning("Database connection check failed")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="GBP/USD Day Trading Application",
    description="Professional day trading system for GBP/USD",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle global exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = check_db_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected"
    }


# Version endpoint
@app.get("/version")
async def get_version():
    """Get application version."""
    return {
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# Include routers
app.include_router(data.router)
app.include_router(strategies.router)
app.include_router(backtesting.router)
app.include_router(trading.router)
app.include_router(analytics.router)
app.include_router(indicators.router)

# WebSocket endpoint
app.add_api_route("/ws", websocket_endpoint, methods=["GET"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development"
    )

