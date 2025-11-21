from fastapi import FastAPI
from app.api.routes import router as api_router
from app.config import settings
import uvicorn
import os

app = FastAPI(title="video-gen-backend")
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    should_reload = settings.ENVIRONMENT == "development"

    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT, 
        reload=should_reload
    )