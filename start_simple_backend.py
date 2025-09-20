#!/usr/bin/env python3
"""
Simple backend startup script
"""

import os
import sys
import subprocess

def main():
    """Start the enhanced backend."""
    print("🚀 Starting Legal AI Backend...")
    
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Start the enhanced backend
        subprocess.run([sys.executable, "enhanced_main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
