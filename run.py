"""Application entry point."""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    uvicorn.run(
        "backend.app:create_app",
        factory=True,
        host='0.0.0.0',
        port=8000,  # Changed from 5000 to avoid conflict with macOS ControlCenter
        reload=True  # Auto-reload on code changes
    )
