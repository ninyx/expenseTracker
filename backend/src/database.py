# src/database.py
"""Database connection and management module."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from mongomock import MongoClient as MockMongoClient
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from src.config.settings import get_database_settings, Environment, COLLECTIONS
from src.config.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseInitializationError,
    CollectionError
)

# Global client and db - made private to enforce usage through functions
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def connect_to_mongo() -> AsyncIOMotorClient:
    """
    Connect to MongoDB — mock for tests, real async client otherwise.
    
    Returns:
        AsyncIOMotorClient: The database client
        
    Raises:
        DatabaseConnectionError: If connection fails
    """
    global _client, _db
    settings = get_database_settings()

    try:
        if settings.APP_ENV == Environment.TEST:
            _client = MockMongoClient()
        else:
            loop = asyncio.get_running_loop()
            _client = AsyncIOMotorClient(
                settings.connection_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Verify connection
            await _client.admin.command('ping')
        
        _db = _client[settings.database_name]
        print(f"✅ Connected to MongoDB: {settings.database_name} (ENV: {settings.APP_ENV})")
        return _client
    
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to connect to MongoDB: {str(e)}") from e

async def get_db() -> AsyncIOMotorDatabase:
    """
    Get the current MongoDB database instance.
    
    This function supports dependency override in tests.
    In production, it returns the global database instance.
    In tests, FastAPI's dependency_overrides will provide the test database.
    
    Returns:
        AsyncIOMotorDatabase: The database instance
        
    Raises:
        DatabaseInitializationError: If database is not initialized
    """
    global _db
    if _db is None:
        try:
            await connect_to_mongo()
        except DatabaseConnectionError as e:
            raise DatabaseInitializationError("Database not initialized and connection failed") from e
    return _db

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Context manager for database operations.
    
    Usage:
        async with get_db_context() as db:
            result = await db.collection.find_one(...)
    """
    db = await get_db()
    try:
        yield db
    except Exception as e:
        # Log error here when logging is implemented
        raise DatabaseError(f"Database operation failed: {str(e)}") from e

async def get_client() -> AsyncIOMotorClient:
    """
    Get the current MongoDB client instance.
    
    Returns:
        AsyncIOMotorClient: The database client
        
    Raises:
        DatabaseInitializationError: If client is not initialized
    """
    global _client
    if _client is None:
        try:
            await connect_to_mongo()
        except DatabaseConnectionError as e:
            raise DatabaseInitializationError("Client not initialized and connection failed") from e
    return _client

def get_collection(collection_name: str) -> AsyncIOMotorDatabase:
    """
    Get a specific collection by name.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection: The MongoDB collection
        
    Raises:
        CollectionError: If collection is not defined or database not initialized
    """
    if collection_name not in COLLECTIONS.values():
        raise CollectionError(f"Collection {collection_name} is not defined")
    if _db is None:
        raise DatabaseInitializationError("Database not initialized")
    return _db[collection_name]

async def close_mongo_connection() -> None:
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("👋 MongoDB connection closed")