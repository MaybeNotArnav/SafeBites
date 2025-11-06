"""
Defines custom exception classes used throughout the SafeBites backend.

These exceptions are used to standardize error handling for API endpoints
and internal services:

- NotFoundException: Raised when a requested resource is not found in the database.
- BadRequestException: Raised when a request is malformed or contains invalid data.
- DatabaseException: Raised for database-related errors.
- GenericException: Raised for generic or uncategorized exceptions.
- AuthError: Raised for authentication failures (returns HTTP 401).
- ConflictException: Raised for resource conflicts, such as duplicate entries (returns HTTP 409).

Using these exceptions allows consistent error responses and better debugging.
"""
from fastapi import HTTPException

class NotFoundException(Exception):
    """Raised when a resource is not found in the database."""
    def __init__(self, name: str):
        self.name = name

class BadRequestException(Exception):
    """Raised when a request is malformed or contains invalid data."""
    def __init__(self, message: str):
        self.message = message

class DatabaseException(Exception):
    """Raised when there is a database-related error."""
    def __init__(self, message: str):
        self.message = message
    
class GenericException(Exception):
    """Raised for any other generic exceptions."""
    def __init__(self, message: str):
        self.message = message

class AuthError(HTTPException):
    """Raised when there is an authentication error."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)

class ConflictException(HTTPException):
    """Raised for 409 conflicts (duplicate username/dish)."""
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)
