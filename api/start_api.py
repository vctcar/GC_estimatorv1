#!/usr/bin/env python3
"""
Startup script for the GC Estimator FastAPI server
"""

import uvicorn
import sys
import os

# Add the parent directory to Python path to import estimator modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

if __name__ == "__main__":
    print("🚀 Starting GC Estimator API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/")
    print("⚡ Server running on: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
