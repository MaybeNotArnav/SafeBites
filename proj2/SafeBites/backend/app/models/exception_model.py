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

class AuthError(HTTPException):
    """Raised when there is an authentication error."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)