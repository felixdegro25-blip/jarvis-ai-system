"""
JARVIS AI Backend Server
- FastAPI Server für Web-Apps
- SQLite Datenbank
- Real-time KI Processing
- Background AI Worker Thread
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from backend.database import init_database
from backend.config import settings
from backend.api_routes import router
from backend.ai_worker import start_ai_worker

# Load environment variables
load_dotenv()

# ============ FASTAPI SETUP ============
app = FastAPI(
    title="JARVIS Control Server",
    description="Iron Man Style AI Control System",
    version="1.0.0"
)

# Enable CORS for Web-Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ INITIALIZATION ============
@app.on_event("startup")
async def startup_event():
    """On server startup"""
    print("\n" + "="*50)
    print("🚀 JARVIS Server Starting...")
    print("="*50)
    
    # Initialize database
    init_database()
    print(f"✅ Database: {settings.DATABASE_PATH}")
    
    # Start AI background worker
    start_ai_worker()
    print("✅ AI Worker started")
    
    print("✅ All systems ready")
    print(f"🌐 Server running on: http://0.0.0.0:{settings.SERVER_PORT}")
    print("="*50 + "\n")

# ============ ROUTES ============
app.include_router(router, prefix="/api", tags=["API"])

@app.get("/")
async def root():
    """Health Check"""
    from datetime import datetime
    return {
        "status": "JARVIS Control Server Online ✅",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {"status": "healthy", "service": "jarvis-ai-system"}

# ============ STATIC FILES ============
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ============ MAIN ============
if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
