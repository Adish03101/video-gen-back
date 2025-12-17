from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# IMPORTS
from app.api.routes import router
from app.database.database import create_db_and_tables  # <--- NEW IMPORT

# ==========================================
# LIFESPAN (Startup/Shutdown Logic)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ONCE when server starts
    create_db_and_tables()
    print("Startup: Database tables created.")
    yield
    # (Optional) Code here runs when server shuts down

# ==========================================
# APP DEFINITION
# ==========================================
app = FastAPI(
    title="Story AI API",
    description="Backend for the AI Story Application",
    version="1.0.0",
    lifespan=lifespan  # <--- CRITICAL: Pass the lifespan here
)

# ==========================================
# CORS CONFIGURATION
# ==========================================
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTER REGISTRATION
# ==========================================
app.include_router(router, prefix="/api/v1", tags=["Story Generation"])

# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Story AI Engine is Running"}

# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)