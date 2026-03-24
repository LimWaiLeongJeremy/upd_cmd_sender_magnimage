"""
Uvicorn server entry point. Run this to start the API server.

Usage:
    python server.py

Or using Uvicorn directly (recommended for production):
    uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

WHY TWO WAYS?
  `python server.py`        → convenience during development
  `uvicorn api.app:app ...` → explicit, used in Docker CMD and production

The `--reload` flag makes Uvicorn watch for file changes and restart
automatically. Use it during development, never in production.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )