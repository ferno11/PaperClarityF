# Legal Document Analysis AI System

A comprehensive AI-powered legal document analysis system that provides clause summarization, risk assessment, and interactive Q&A capabilities.

## 🚀 Features

- **Document Upload & Processing**: Support for PDF, DOC, and DOCX files
- **AI-Powered Clause Analysis**: Automatic clause extraction and summarization
- **Risk Assessment**: Intelligent risk classification (High/Medium/Low) for each clause
- **Interactive Chat**: Ask questions about your documents with AI-powered responses
- **Semantic Search**: Find relevant clauses using advanced embedding technology
- **Privacy-First**: Automatic document deletion after 24 hours
- **Modern UI**: Responsive design with dark/light mode support

## 📁 Project Structure

```
genai_legal/
├── src/
│   ├── backend/                 # FastAPI backend server
│   │   ├── main.py             # Main FastAPI application
│   │   ├── utils.py            # Document processing utilities
│   │   ├── summarize_clauses.py # AI clause analysis
│   │   └── requirements.txt    # Python dependencies
│   ├── frontend/               # Next.js frontend application
│   │   ├── src/
│   │   │   ├── app/           # Next.js app router
│   │   │   ├── components/    # React components
│   │   │   ├── lib/           # Utilities and types
│   │   │   └── providers/     # Context providers
│   │   ├── package.json       # Node.js dependencies
│   │   └── next.config.ts     # Next.js configuration
│   └── shared/                 # Shared types and utilities
├── docs/                       # Documentation and sample documents
├── scripts/                    # Deployment and utility scripts
├── tests/                      # Test files
├── uploads/                    # Temporary file storage (auto-deleted)
├── results/                    # Analysis results cache (auto-deleted)
└── README.md                   # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Git** for version control

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd src/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

5. **Run the backend server:**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd src/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## 🚀 Quick Start

1. **Start the backend server:**
   ```bash
   cd src/backend
   python main.py
   ```

2. **Start the frontend (in a new terminal):**
   ```bash
   cd src/frontend
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

4. **Upload a document:**
   - Click "Upload Document" on the dashboard
   - Select a PDF, DOC, or DOCX file
   - Wait for analysis to complete

5. **Explore the results:**
   - View clause summaries and risk assessments
   - Ask questions in the chat interface
   - Download or share results

## 🔧 API Endpoints

### Core Endpoints

- `POST /api/upload` - Upload a document for analysis
- `POST /api/analyze/{file_id}` - Trigger analysis for uploaded document
- `GET /api/results/{file_id}` - Get analysis results
- `POST /api/chat/{file_id}` - Chat with the document
- `GET /health` - Health check endpoint

### Example Usage

```bash
# Upload a document
curl -X POST "http://localhost:8001/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Get analysis results
curl "http://localhost:8001/api/results/{file_id}"

# Chat with document
curl -X POST "http://localhost:8001/api/chat/{file_id}" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key terms?"}'
```

## 🧠 AI Features

### Clause Analysis
- **Automatic Extraction**: Identifies and extracts individual clauses
- **Smart Summarization**: AI-powered summaries of complex legal text
- **Risk Classification**: Intelligent risk assessment (High/Medium/Low)

### Interactive Chat
- **Semantic Search**: Find relevant clauses using vector embeddings
- **Context-Aware Responses**: AI answers based on document content
- **Reference Tracking**: Shows which clauses support each answer

### Privacy & Security
- **Auto-Deletion**: Documents automatically deleted after 24 hours
- **No Persistent Storage**: Analysis results are cached temporarily only
- **Secure Processing**: All processing happens in isolated environment

## 🎨 UI Features

### Dashboard
- **Document Upload**: Drag-and-drop file upload with validation
- **Recent Documents**: Quick access to previously analyzed files
- **Risk Overview**: Visual charts showing risk distribution

### Analysis View
- **Clause Cards**: Expandable cards with summaries and risk levels
- **Risk Dashboard**: Pie charts and statistics
- **Interactive Chat**: Real-time Q&A with document

### Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Dark/Light Mode**: Toggle between themes
- **Accessibility**: WCAG compliant with keyboard navigation

## 🔒 Privacy & Security

- **Temporary Storage**: Files stored only during analysis
- **Auto-Deletion**: 24-hour automatic cleanup
- **No Data Mining**: No user data is collected or stored
- **Local Processing**: All AI processing happens on your server

## 🧪 Testing

### Backend Tests
```bash
cd src/backend
pytest tests/
```

### Frontend Tests
```bash
cd src/frontend
npm test
```

## 📚 Documentation

- **API Documentation**: Available at `http://localhost:8001/docs`
- **Component Library**: See `src/frontend/src/components/`
- **Type Definitions**: See `src/frontend/src/lib/types.ts`

## 🚀 Deployment

### Production Backend
```bash
cd src/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Production Frontend
```bash
cd src/frontend
npm run build
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the API documentation at `http://localhost:8001/docs`

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added semantic search and improved chat
- **v1.2.0** - Enhanced UI and mobile responsiveness
- **v1.3.0** - Added auto-deletion and privacy features

---

**Built with ❤️ for legal professionals and document analysis**