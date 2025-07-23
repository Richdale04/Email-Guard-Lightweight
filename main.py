#!/usr/bin/env python3
"""
Startup script for Email Guard Backend on Render
"""
import uvicorn
import os
from backend.app import app

if __name__ == "__main__":
    # Get port from environment variable (Render sets PORT)
    port = int(os.environ.get("PORT", 5000))

    # Run the FastAPI app
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
