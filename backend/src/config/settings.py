"""Application configuration and settings."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from enum import Enum
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

class DatabaseSettings(BaseSettings):
    """Database-specific settings."""
    MONGO_USER: str = "root"
    MONGO_PASS: str = "password"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: str = "27017"
    MONGO_URI: Optional[str] = None
    APP_ENV: Environment = Environment.DEVELOPMENT

    @property
    def database_name(self) -> str:
        """Get the database name based on environment."""
        return "expenseTracker_test" if self.APP_ENV == Environment.TEST else "expenseTracker"
    
    @property
    def connection_uri(self) -> str:
        """Get the MongoDB connection URI."""
        if self.MONGO_URI:
            return self.MONGO_URI
            
        # Add ?authSource=admin to the URI for proper authentication
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource=admin"

    def dict(self, *args, **kwargs):
        """Override dict to exclude None values."""
        kwargs["exclude_none"] = True
        return super().dict(*args, **kwargs)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        use_enum_values=True,
        env_prefix="",  # No prefix for cleaner mapping
        env_nested_delimiter="__",
        extra="ignore",
        aliases={
            "MONGO_USER": "MONGO_INITDB_ROOT_USERNAME",
            "MONGO_PASS": "MONGO_INITDB_ROOT_PASSWORD"
        }
    )

@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings."""
    return DatabaseSettings()

# Collection names - could be moved to a separate constants file if it grows
COLLECTIONS = {
    "transactions": "transactions"
}