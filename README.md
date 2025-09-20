# 🏛️ GenAI Legal Tool

A comprehensive legal document analysis platform that uses AI to process, analyze, and provide insights on legal documents.

## ✨ Features

- **📄 Document Upload**: Upload legal documents for analysis
- **🔍 Clause Analysis**: Automatically split documents into individual clauses
- **⚠️ Risk Assessment**: Classify clauses as High/Medium/Low risk
- **🏷️ Entity Extraction**: Identify money, dates, percentages, and timeframes
- **💬 Chat Interface**: Ask questions about your documents
- **🎨 Modern UI**: Beautiful, responsive interface with risk color coding

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd genai_legal
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   venv\bin\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend** (Terminal 1)
   ```bash
   python run.py
   ```
   Backend will be available at: http://localhost:8000

2. **Start the Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at: http://localhost:3000

## 🏗️ Project Structure

```
genai_legal/
├── backend/                 # Backend server
│   ├── server.py           # Main server implementation
│   ├── main.py             # Original FastAPI implementation
│   ├── qa.py               # Q&A functionality
│   └── utils.py            # Utility functions
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App pages
│   │   ├── components/    # UI components
│   │   ├── lib/           # Utilities and types
│   │   └── hooks/         # React hooks
│   ├── package.json       # Dependencies
│   └── next.config.ts     # Next.js config
├── docs/                   # Sample documents and processed data
├── ai_models/              # AI model implementations
├── run.py                  # Main entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 API Endpoints

### Backend API (http://localhost:8000)

- `GET /` - API information
- `GET /health` - Health check
- `POST /upload` - Upload document for analysis
- `GET /clauses/{doc_id}` - Get clauses for a document
- `POST /ask` - Ask questions about a document

### Example Usage

   ```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST -F "file=@document.txt" http://localhost:8000/upload

# Get clauses
curl http://localhost:8000/clauses/{doc_id}

# Ask question
curl -X POST -H "Content-Type: application/json" \
  -d '{"doc_id": "uuid", "question": "What is the rent amount?"}' \
  http://localhost:8000/ask
```

## 🎨 Frontend Features

- **Document Upload**: Drag-and-drop interface
- **Clause Cards**: Interactive cards with risk color coding
  - 🔴 High Risk
  - 🟡 Medium Risk  
  - 🟢 Low Risk
- **Risk Overview**: Pie chart showing risk distribution
- **Chat Panel**: Real-time Q&A about documents
- **Document Preview**: Side-by-side document viewing

## 🧠 AI Features

### Risk Classification
The system automatically classifies clauses based on keywords:

- **High Risk**: termination, liability, damages, penalty, breach, lawsuit, eviction, foreclosure, default
- **Medium Risk**: modify, change, restrict, limit, notice, interest, late fee, maintenance
- **Low Risk**: contact, inform, provide, communication, address, signature, governing law

### Entity Extraction
Automatically identifies:
- **Money**: $1,200, $500, etc.
- **Percentages**: 5%, 10%, etc.
- **Dates**: 01/01/2024, 12/31/2024, etc.
- **Timeframes**: 30 days, 60 days, 1 year, etc.

## 🛠️ Development

### Backend Development
The backend uses a simple HTTP server implementation for reliability and easy deployment.

### Frontend Development
The frontend is built with:
- **Next.js 15** with TypeScript
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **Recharts** for data visualization

### Adding New Features
1. Backend: Add new endpoints in `backend/server.py`
2. Frontend: Add new components in `frontend/src/components/`
3. Types: Update types in `frontend/src/lib/types.ts`

## 📝 Sample Documents

The `docs/` directory contains sample legal documents for testing:
- Rental agreements
- Employment contracts
- Insurance policies
- Loan agreements
- NDAs
- Terms of service
- Vendor agreements

## 🔒 Security Notes

- The current implementation uses in-memory storage for demo purposes
- For production use, implement proper database storage
- Add authentication and authorization as needed
- Validate and sanitize all user inputs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API health: http://localhost:8000/health
2. Verify both servers are running
3. Check the browser console for errors
4. Review the terminal output for backend errors

---

**Happy analyzing! 🎉**