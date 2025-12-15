from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the router we just built
from app.api.routes import router

app = FastAPI(
    title="Story AI API",
    description="Backend for the AI Story Application",
    version="1.0.0"
)

# ==========================================
# CORS CONFIGURATION (Critical for Frontend)
# ==========================================
origins = [
    "http://localhost:3000", # React default
    "http://localhost:5173", # Vite default
    "http://127.0.0.1:5173", # Vite alternative
    "*"                      # Allow all (easiest for prototype)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allow Content-Type, Authorization, etc.
)

# ==========================================
# ROUTER REGISTRATION
# ==========================================
# We mount the router at /api/v1 so your URL is like:
# http://localhost:8000/api/v1/generate/ideas
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
    # This allows you to run via 'python app/main.py' as well
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)