#!/usr/bin/env python3
"""
Entry point script for the GenAI Legal Document Analysis Tool.
This script starts the backend server.
"""
import os
import sys

def main():
    # Add the backend directory to the Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    # Import and run the server
    from server import run_server
    run_server()

if __name__ == "__main__":
    main()