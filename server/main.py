from fastapi import FastAPI
from controller.user import api_router
from utils.config.db import Base, engine
import logger
import uvicorn

app = FastAPI(
    title="Facebook-like API",
    description="An API for managing users, contacts, chats, and statuses similar to Facebook.",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(api_router, prefix="/api/v1")  # Versioning our API

# adding logging to a route
@app.get("/")
async def root():
    logger.logger.info("Root endpoint called")
    return {"message": "Hello World"}

# Log startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.logger.info("Application shutdown")

# Server configuration
if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8001, reload= True, workers= 2)