"""
FastAPI application factory.

WHY A FACTORY FUNCTION (create_app)?
  Instead of creating `app = FastAPI()` at module level, we use a
  create_app() function. This pattern lets you:
    - Create the app with different configs (test vs production)
    - Import app in tests without side effects
    - Phase 3: pass config into the app from Docker env vars

  It's a small habit that pays off when the project grows.
"""


import logging

from fastapi import FastAPI

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
    app.add.middleware(
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
    
    # -------------------------------------------------------------------
    # Health check endpoint 
    # -------------------------------------------------------------------
    @app.get("/health", tags=["System"])
    def health_check() -> dict:
        return {"status": "healthy", "service": "LED Controller API"}
    
    logger.info("LED Controller API initialization complete.")
    return app

# Module-Level app instance for Uvicorn to import
app = create_app()
