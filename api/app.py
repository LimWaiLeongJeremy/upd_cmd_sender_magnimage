"""
api/app.py
-----------
Updated for Phase 3: serves the built React static files in production.

HOW IT WORKS:
  In development  — frontend/dist doesn't exist, FastAPI serves only the API.
                    You run React separately with npm run dev.
  In Docker       — frontend/dist exists (built during Docker image creation),
                    FastAPI serves the React app AND the API from port 8000.

The StaticFiles mount MUST be added last — after all routers.
If it were added first, it would intercept /api/* routes.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import brightness, devices
from constants import LOG_FILE, LOG_NAME
from utils.logger import setup_logger


def create_app() -> FastAPI:
    """
    Construct and configure the FastAPI application instance.

    Returns:
        Fully configured FastAPI app, ready to be served by Uvicorn.
    """
    # Initialise logging once at app startup
    setup_logger(LOG_NAME, LOG_FILE)
    logger = logging.getLogger(LOG_NAME)
    logger.info("Initialising LED Controller API...")
    
    app = FastAPI(
        title="LED Controller API",
        description=(
            "REST API for controlling Magnimage FW16-C LED Video Controllers. "
            "Supports absolute brightness control and gradual brightness ramping "
            "on individual devices or device groups."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # -------------------------------------------------------------------
    # CORS Middleware
    # -------------------------------------------------------------------
    # CORS (Cross-Origin Resource Sharing) controls which domains can
    # call your API from a browser. Without this, your React frontend
    # running on localhost:5173 would be BLOCKED from calling your API
    # on localhost:8000 — browsers enforce this by default.
    #
    # allow_origins=["*"] = any origin can call the API (dev only).
    # For production: replace "*" with your exact frontend domain.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # -------------------------------------------------------------------
    # Include API routers
    # -------------------------------------------------------------------
    app.include_router(brightness.router)
    app.include_router(devices.router)  
    
    # -------------------------------------------------------------------
    # Health check endpoint 
    # -------------------------------------------------------------------
    @app.get("/health", tags=["System"])
    def health_check() -> dict:
        return {"status": "healthy", "service": "LED Controller API"}
    
    # ── Serve built React app (production / Docker only) ──
    # Checks if the build output exists before mounting.
    # This keeps the dev workflow unchanged — no build needed locally.
    dist_path = Path(__file__).parent.parent / "frontend" / "dist"
    if dist_path.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(dist_path), html=True),
            name="frontend",
        )
        logger.info(f"Serving React build from {dist_path}")
    else:
        logger.info("No frontend/dist found — API-only mode (dev)")

    
    logger.info("LED Controller API initialization complete.")
    return app

# Module-Level app instance for Uvicorn to import
app = create_app()
