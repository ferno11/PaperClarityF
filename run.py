#!/usr/bin/env python
"""
Entry point script for the GenAI Legal Document Analysis Tool.
This script starts the FastAPI server from the backend directory.
"""
import os
import sys
import uvicorn

def main():
    # Add the project root to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import the app from the backend module
    from backend.main import app
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()