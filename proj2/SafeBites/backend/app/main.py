import logging, os
import threading
from fastapi import FastAPI
from app.routers import restaurant_router,dish_router, user_router
from app.services.faiss_service import build_faiss_from_db
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
from app.routers import dish_router, user_router
from app.services.exception_service import register_exception_handlers
import uvicorn

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Welcome to Safebites....")
logger.info("Setting up routers....")
# app.include_router(restaurant_router.router)
app.include_router(dish_router.router)
app.include_router(user_router.router)


logger.info("Registering Exception Handlers....")
register_exception_handlers(app)

@app.on_event("startup")
async def initialize_faiss():
    """
    On startup, verify the FAISS index exists.
    If missing, trigger an asynchronous background rebuild.
    """
    index_path = "faiss_index_restaurant"

    if not os.path.exists(index_path):
        logger.warning("FAISS index not found. Triggering rebuild from database...")
        threading.Thread(target=build_faiss_from_db,daemon=True).start()
    else:
        logger.info("FAISS index found and ready to use.")

@app.get("/")
def root():
    return {"message":"Welcome to SafeBites API"}
