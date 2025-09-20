# 🏛️ Paper Clarity - Legal AI Document Analysis

> **AI-powered legal document analysis with intelligent risk assessment and Q&A**

[![Backend Status](https://img.shields.io/badge/Backend-Running-green)](http://localhost:8001/health)
[![Frontend Status](https://img.shields.io/badge/Frontend-Running-blue)](http://localhost:3000)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **Overview**

Paper Clarity is a comprehensive legal document analysis platform that uses AI to:
- **Analyze legal documents** and extract clauses
- **Assess risk levels** (High/Medium/Low) using advanced heuristics
- **Provide intelligent Q&A** with semantic search and reference tracking
- **Ensure privacy** with automatic 24-hour file deletion

## ✨ **Key Features**

### 🔍 **Document Analysis**
- **Multi-format support**: PDF, DOC, DOCX
- **Intelligent clause extraction** and splitting
- **AI-powered summarization** of each clause
- **Advanced risk classification** with scoring system

### 📊 **Risk Assessment**
- **Visual risk dashboard** with pie charts and statistics
- **Color-coded clause cards** (red=high, yellow=medium, green=low)
- **Overall risk scoring** (0-100 scale)
- **Detailed risk breakdown** with counts and percentages

### 🤖 **AI Chat Interface**
- **Semantic search** using sentence transformers
- **Natural language Q&A** about document content
- **Reference tracking** showing which clauses were used
- **Fallback keyword search** for reliability

### 🔒 **Privacy & Security**
- **Automatic file deletion** after 24 hours
- **No permanent storage** of sensitive documents
- **Secure processing** with temporary file handling
- **Clear privacy disclaimers**

### 🎨 **Modern UI/UX**
- **Responsive design** for mobile and desktop
- **Dark mode support** with theme switching
- **Drag & drop upload** with validation
- **Real-time processing** indicators
- **Accessibility features** throughout

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

### **1. Clone Repository**
```bash
git clone https://github.com/Endless-Mrianl/genai_legal.git
cd genai_legal
```

### **2. Backend Setup**
```bash
# Install Python dependencies
py -m pip install fastapi uvicorn python-multipart sentence-transformers torch requests

# Start backend server
py backend/main.py
```
**Backend runs on**: http://localhost:8001

### **3. Frontend Setup**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start development server
npm run dev
```
**Frontend runs on**: http://localhost:3000

### **4. Access the Application**
- **Main App**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📖 **Usage Guide**

### **1. Upload Document**
- Navigate to the dashboard
- Drag & drop or click to select a legal document
- Supported formats: PDF, DOC, DOCX (max 10MB)
- Wait for upload confirmation

### **2. Analyze Document**
- Click "Upload and Process" to start analysis
- System will extract text, split clauses, and assess risks
- Processing typically takes 10-30 seconds

### **3. Review Results**
- **Risk Dashboard**: View overall risk distribution and score
- **Clause Cards**: Browse individual clauses with summaries
- **Expand Details**: Click to see full original text
- **Copy Text**: Use copy buttons for easy reference

### **4. Ask Questions**
- Use the chat panel to ask questions about the document
- Try questions like:
  - "What are the penalty clauses?"
  - "What are the termination conditions?"
  - "What are the payment terms?"
- View references to see which clauses were used

## 🏗️ **Architecture**

### **Backend (FastAPI)**
```
backend/
├── main.py              # Main API server
├── utils.py             # Document processing utilities
└── qa.py               # Q&A and semantic search
```

**Key Endpoints:**
- `POST /api/upload` - Upload document
- `POST /api/analyze/{file_id}` - Analyze document
- `GET /api/results/{file_id}` - Get analysis results
- `POST /api/chat/{file_id}` - Chat with document
- `GET /health` - Health check

### **Frontend (Next.js + React)**
```
frontend/
├── src/
│   ├── app/                    # Next.js app router
│   ├── components/             # React components
│   │   ├── dashboard/          # Dashboard components
│   │   └── ui/                # UI component library
│   └── lib/                   # Utilities and API
```

**Key Components:**
- `DocumentUpload` - File upload with validation
- `RiskDashboard` - Risk visualization and statistics
- `ClauseCard` - Individual clause display
- `ChatPanel` - AI Q&A interface
- `Disclaimer` - Privacy and legal notices

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Backend
NEXT_PUBLIC_API_URL=http://localhost:8001

# Optional: OpenAI API key for enhanced AI
OPENAI_API_KEY=your_openai_key_here
```

### **Risk Classification**
The system uses advanced heuristics to classify risk levels:

**High Risk Indicators:**
- Penalty, fine, termination, breach, default
- Legal action, lawsuit, litigation, court
- Liability, damages, indemnify, warranty
- Criminal, prosecution, illegal, unlawful

**Medium Risk Indicators:**
- Notice, payment, maintenance, repair
- Modification, amendment, change, update
- Schedule, timeline, deadline, expiration
- Condition, requirement, obligation

**Low Risk Indicators:**
- Information, data, record, document
- Reference, example, sample, template
- Description, explanation, clarification
- Purpose, objective, goal, scope

## 🧪 **Testing**

### **Backend Testing**
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test upload
curl -X POST -F "file=@test.pdf" http://localhost:8001/api/upload

# Test analysis
curl -X POST http://localhost:8001/api/analyze/{file_id}

# Test results
curl http://localhost:8001/api/results/{file_id}

# Test chat
curl -X POST -H "Content-Type: application/json" \
  -d '{"question":"What are the penalty clauses?"}' \
  http://localhost:8001/api/chat/{file_id}
```

### **Frontend Testing**
- Open http://localhost:3000
- Upload a test document
- Verify all components render correctly
- Test chat functionality
- Check responsive design

## 📊 **Performance**

### **Backend Performance**
- **Upload**: < 5 seconds for 10MB files
- **Analysis**: 10-30 seconds depending on document size
- **Chat**: < 2 seconds for semantic search
- **Memory**: ~200MB with sentence transformers

### **Frontend Performance**
- **Initial Load**: < 3 seconds
- **Navigation**: < 1 second
- **Upload**: Real-time progress indication
- **Responsive**: Works on mobile and desktop

## 🔒 **Security & Privacy**

### **Data Handling**
- Files stored temporarily in `uploads/` directory
- Results cached in `results/` directory
- Automatic cleanup after 24 hours
- No permanent storage of sensitive data

### **API Security**
- CORS enabled for frontend communication
- Input validation on all endpoints
- Error handling without data leakage
- Rate limiting (can be added)

### **Privacy Features**
- Clear disclaimers about AI-generated content
- Automatic file deletion
- No user data collection
- Transparent processing

## 🚀 **Deployment**

### **Production Backend**
```bash
# Install production dependencies
pip install fastapi uvicorn[standard] sentence-transformers

# Run with production server
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### **Production Frontend**
```bash
# Build for production
npm run build

# Start production server
npm start
```

### **Docker Deployment**
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY frontend/ .
RUN npm install && npm run build
CMD ["npm", "start"]
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **FastAPI** for the excellent Python web framework
- **Next.js** for the React-based frontend framework
- **Sentence Transformers** for semantic search capabilities
- **Tailwind CSS** for the beautiful UI components
- **Radix UI** for accessible component primitives

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/Endless-Mrianl/genai_legal/issues)
- **Documentation**: [API Docs](http://localhost:8001/docs)
- **Demo**: [Live Demo](http://localhost:3000)

---

**🎉 Ready to analyze your legal documents with AI!**