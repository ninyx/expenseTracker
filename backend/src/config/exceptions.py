"""Custom exceptions for database operations."""

class DatabaseError(Exception):
    """Base class for database-related exceptions."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to the database."""
    pass

class DatabaseInitializationError(DatabaseError):
    """Raised when database initialization fails."""
    pass

class CollectionError(DatabaseError):
    """Raised when operations on collections fail."""
    pass