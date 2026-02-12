"""Main entry point for Documentation Generator API."""

import uvicorn
from app.__main__ import app

if __name__ == "__main__":
    uvicorn.run(
        "app.__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
