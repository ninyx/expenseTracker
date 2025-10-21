from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import connect_to_mongo, close_mongo_connection, get_db
from src.db_indexes import create_indexes
from src.routes.transactionsRoute import router as transaction_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events for the FastAPI application.
    """
    # Startup: Connect to MongoDB and initialize indexes
    await connect_to_mongo()
    
    db = await get_db()
    if db is None:
        raise RuntimeError("MongoDB connection not initialized before creating indexes.")
    
    await create_indexes()
    print("🚀 Server startup complete")
    
    yield
    
    # Shutdown: Close MongoDB connection
    from src.database import client
    if client:
        client.close()
        print("🛑 MongoDB client closed")

app = FastAPI(lifespan=lifespan)
app.include_router(transaction_router)

