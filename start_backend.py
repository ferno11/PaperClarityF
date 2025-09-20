#!/usr/bin/env python3
"""
Start the GenAI Legal Tool Backend Server.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from server import run_server

if __name__ == "__main__":
    print("🚀 Starting GenAI Legal Tool Backend...")
    run_server()
