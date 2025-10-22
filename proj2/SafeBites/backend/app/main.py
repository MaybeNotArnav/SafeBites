import logging
from fastapi import FastAPI
from app.routers import restaurant_router, dish_router, user_router
from app.services.exception_service import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
from .config import setup_logging

app = FastAPI(title="SafeBites")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080","http://localhost:8000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Welcome to Safebites....")
logger.info("Setting up routers....")
app.include_router(restaurant_router.router)
app.include_router(dish_router.router)
app.include_router(user_router.router)

logger.info("Registering Exception Handlers....")
register_exception_handlers(app)

@app.get("/")
def root():
    return {"message":"Welcome to SafeBites API"}
