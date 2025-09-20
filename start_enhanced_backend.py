#!/usr/bin/env python3
"""
Start the Enhanced Legal Document Analysis Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-multipart',
        'pypdfium2',
        'python-docx',
        'openai',
        'scikit-learn',
        'numpy',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has OpenAI API key."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating template...")
        with open(".env", "w") as f:
            f.write("# OpenAI API Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("\n# Optional: Customize auto-delete time (in hours)\n")
            f.write("AUTO_DELETE_HOURS=24\n")
        print("📝 Please edit .env file and add your OpenAI API key")
        return False
    
    # Check if API key is set
    with open(".env", "r") as f:
        content = f.read()
        if "your_openai_api_key_here" in content or "OPENAI_API_KEY=" not in content:
            print("⚠️  Please set your OpenAI API key in .env file")
            return False
    
    return True

def main():
    """Main function to start the enhanced backend."""
    print("🚀 Starting Enhanced Legal Document Analysis Backend")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing packages and try again")
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("\n❌ Please configure your environment and try again")
        sys.exit(1)
    
    # Start the enhanced backend
    print("\n✅ All checks passed!")
    print("🤖 Starting AI-powered backend...")
    print("🔒 Auto-delete enabled for privacy")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("\n" + "=" * 60)
    
    try:
        # Change to backend directory and run
        os.chdir("backend")
        subprocess.run([
            sys.executable, "enhanced_main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Backend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting backend: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
