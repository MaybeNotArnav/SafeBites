from fastapi import FastAPI
from SafeBites.backend.app.routers import restaurant_router, dish_router, user_router
from app.services.exception_service import register_exception_handlers
import uvicorn

app = FastAPI(title="SafeBites")

app.include_router(restaurant_router.router)
app.include_router(dish_router.router)
app.include_router(user_router.router)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message":"Welcome to SafeBites API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

