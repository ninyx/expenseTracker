from fastapi import FastAPI
from src.database import connect_to_mongo, close_mongo_connection
from src import database as db  # again, import the module
from src.db_indexes import create_indexes
from src.routes.transactionsRoute import router as transaction_router

app = FastAPI()

app.include_router(transaction_router)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

    if db.db is None:
        raise RuntimeError("MongoDB connection not initialized before creating indexes.")
    
    await create_indexes()

    print("🚀 Server startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
