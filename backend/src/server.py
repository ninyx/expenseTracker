# src/server.py
"""FastAPI application instance and configuration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.database import connect_to_mongo, close_mongo_connection
from src.db_indexes import create_indexes
from src.routes.transactionsRoute import router as transaction_router
from src.config.exceptions import DatabaseConnectionError, DatabaseInitializationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events for the FastAPI application.
    
    In test mode (when dependency_overrides is set), this will skip
    production database initialization.
    """
    # Check if we're in test mode (dependency overrides are set)
    is_test_mode = bool(app.dependency_overrides)
    
    if not is_test_mode:
        try:
            # Startup: Connect to MongoDB and initialize indexes
            await connect_to_mongo()
            await create_indexes()
            print("🚀 Server startup complete")
        except (DatabaseConnectionError, DatabaseInitializationError) as e:
            print(f"❌ Failed to initialize server: {str(e)}")
            raise
    else:
        print("🧪 Test mode: Skipping production database initialization")
    
    yield
    
    # Shutdown: Close MongoDB connection (only in production mode)
    if not is_test_mode:
        await close_mongo_connection()
        print("👋 Server shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="API for tracking expenses and managing financial transactions",
    version="1.0.0",
    lifespan=lifespan
)

# Exception handlers
@app.exception_handler(DatabaseConnectionError)
async def database_connection_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database connection failed"}
    )

@app.exception_handler(DatabaseInitializationError)
async def database_initialization_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database initialization failed"}
    )

# Include routers
app.include_router(transaction_router)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}