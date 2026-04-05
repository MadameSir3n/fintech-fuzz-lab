"""
FinTech Fuzz Lab
Entry point: starts the payment API target for fuzz testing.

Usage:
    pip install -r requirements.txt
    python main.py          # start the API

    Run fuzz tests:
    python -m pytest tests/ -v

    Or with Docker:
    docker-compose up --build
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
