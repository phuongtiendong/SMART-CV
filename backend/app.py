"""FastAPI application entry point."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import LOG_FILE
from backend.models.database import init_db
from backend.routes.jobs import router as jobs_router
from backend.routes.cvs import router as cvs_router
from utils import ensure_dirs

# Setup logging
ensure_dirs()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Smart CV API",
        description="CV Analysis & Ranking System API",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    init_db()
    
    # Include routers
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(cvs_router, prefix="/api/cvs", tags=["cvs"])
    
    # Serve static files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'frontend/static')
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Serve index page
    @app.get("/")
    async def index():
        template_dir = os.path.join(base_dir, 'frontend/templates')
        index_path = os.path.join(template_dir, 'index.html')
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found"}
    
    return app
