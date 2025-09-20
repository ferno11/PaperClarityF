# 🚀 Legal Document Analysis AI System - Setup Guide

This guide will help you set up the complete Legal Document Analysis AI System on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download here](https://python.org)
- **Node.js 18+** - [Download here](https://nodejs.org)
- **Git** - [Download here](https://git-scm.com)

### Required API Keys
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

## 🛠️ Quick Setup (Automated)

### Windows
```bash
# Run the automated setup script
scripts\setup.bat
```

### macOS/Linux
```bash
# Make the script executable
chmod +x scripts/setup.sh

# Run the automated setup script
./scripts/setup.sh
```

## 🔧 Manual Setup

If you prefer to set up manually or the automated script doesn't work:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/legal-document-analysis-ai.git
cd legal-document-analysis-ai
```

### 2. Backend Setup

#### Navigate to Backend Directory
```bash
cd src/backend
```

#### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Edit the .env file and add your actual OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### Test Backend
```bash
python main.py
```
You should see:
```
🚀 Starting Legal Document Analysis API...
📚 API Documentation: http://localhost:8001/docs
🔒 Auto-delete enabled for privacy (24 hours)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd src/frontend
```

#### Install Dependencies
```bash
npm install
```

#### Test Frontend
```bash
npm run dev
```
You should see:
```
▲ Next.js 15.3.3 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
✓ Ready in X.Xs
```

## 🚀 Running the Application

### Option 1: Run Both Services Separately

#### Terminal 1 - Backend
```bash
cd src/backend
python main.py
```

#### Terminal 2 - Frontend
```bash
cd src/frontend
npm run dev
```

### Option 2: Run Both Services Together
```bash
# From the root directory
npm run dev
```

## 🌐 Access the Application

1. **Frontend**: Open [http://localhost:3000](http://localhost:3000)
2. **Backend API**: Open [http://localhost:8001](http://localhost:8001)
3. **API Documentation**: Open [http://localhost:8001/docs](http://localhost:8001/docs)

## 🧪 Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8001/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "documents_loaded": 0,
  "auto_delete_enabled": true,
  "auto_delete_hours": 24
}
```

### 2. Upload a Test Document
1. Go to [http://localhost:3000](http://localhost:3000)
2. Click "Upload Document"
3. Select a PDF, DOC, or DOCX file
4. Wait for analysis to complete
5. Explore the results and chat interface

## 🔧 Configuration

### Backend Configuration

Edit `src/backend/.env`:
```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Auto-delete Configuration
AUTO_DELETE_HOURS=24

# Logging Configuration
LOG_LEVEL=INFO
```

### Frontend Configuration

Edit `src/frontend/.env.local`:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001

# App Configuration
NEXT_PUBLIC_APP_NAME=Legal Document Analysis AI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Python/Node.js Not Found
```bash
# Check if Python is installed
python --version
# or
python3 --version

# Check if Node.js is installed
node --version
npm --version
```

#### 2. Port Already in Use
```bash
# Kill process using port 8001
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8001 | xargs kill -9
```

#### 3. OpenAI API Key Issues
- Ensure your API key is valid and has sufficient credits
- Check that the key is correctly set in `.env` file
- Verify the key has the necessary permissions

#### 4. Module Not Found Errors
```bash
# Reinstall dependencies
cd src/backend
pip install -r requirements.txt

cd src/frontend
npm install
```

#### 5. Permission Errors
```bash
# Make scripts executable (macOS/Linux)
chmod +x scripts/setup.sh

# Run as administrator (Windows)
# Right-click Command Prompt -> Run as administrator
```

### Getting Help

1. **Check the logs** in the terminal output
2. **Review the API documentation** at [http://localhost:8001/docs](http://localhost:8001/docs)
3. **Check the browser console** for frontend errors
4. **Create an issue** on GitHub with error details

## 📚 Next Steps

Once everything is running:

1. **Read the [README.md](README.md)** for detailed feature documentation
2. **Explore the [API Documentation](http://localhost:8001/docs)** to understand the backend
3. **Check out the [Demo Script](DEMO_SCRIPT.md)** for a guided walkthrough
4. **Review the [Component Library](src/frontend/src/components/)** to understand the frontend

## 🎉 Success!

If you see both services running and can access the application, congratulations! You've successfully set up the Legal Document Analysis AI System.

**Happy analyzing! 🚀**
