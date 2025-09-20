#!/usr/bin/env python3
"""
Quick test to verify backend is working
"""

import requests
import json

def test_backend():
    """Test if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running!")
            print(f"   Status: {data['status']}")
            print(f"   Documents: {data['documents_loaded']}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not reachable: {e}")
        print("   Make sure to start the backend with: python start_enhanced_backend.py")
        return False

if __name__ == "__main__":
    test_backend()
