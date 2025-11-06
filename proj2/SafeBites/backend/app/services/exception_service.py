from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException,AuthError, ConflictException,GenericException


def register_exception_handlers(app):
   @app.exception_handler(NotFoundException)
   async def not_found_handler(request, exc: NotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": str(exc)}  # use str(exc) instead of exc.message
        )
   @app.exception_handler(AuthError)
   async def auth_error_handler(request, exc: AuthError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
   @app.exception_handler(BadRequestException)
   async def bad_request_handler(request, exc: BadRequestException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.message}
        )
   @app.exception_handler(DatabaseException)
   async def database_exception_handler(request, exc: DatabaseException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.message}
        )
   @app.exception_handler(GenericException)
   async def generic_exception_handler(request, exc: GenericException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.message}
        )
   @app.exception_handler(ConflictException)
   async def conflict_exception_handler(request, exc: ConflictException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
