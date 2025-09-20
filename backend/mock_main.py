"""
Mock Legal Document Analysis API
A simple mock backend for testing and demo purposes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime

app = FastAPI(title="Mock Legal Document Analysis API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_documents = {
    "demo-doc-1": {
        "filename": "sample_contract.pdf",
        "clauses": [
            {
                "clause_id": "clause_1",
                "original_text": "This Employment Agreement is entered into on January 1, 2024, between Company Inc. and John Doe.",
                "summary": "This clause establishes the employment relationship and parties involved.",
                "risk_level": "Low",
                "entities": ["Date: 1/1/2024", "Money: $75,000"],
                "word_count": 20
            },
            {
                "clause_id": "clause_2",
                "original_text": "The Employee shall receive a base salary of $75,000 per year, payable in accordance with the Company's regular payroll practices.",
                "summary": "This clause defines the employee's compensation structure and payment terms.",
                "risk_level": "Low",
                "entities": ["Money: $75,000", "Time: 1 year"],
                "word_count": 25
            },
            {
                "clause_id": "clause_3",
                "original_text": "The Employee agrees to maintain the confidentiality of all proprietary information and trade secrets of the Company. This obligation shall survive termination of employment.",
                "summary": "This clause establishes confidentiality obligations that continue after employment ends.",
                "risk_level": "High",
                "entities": ["Time: after termination"],
                "word_count": 30
            },
            {
                "clause_id": "clause_4",
                "original_text": "Either party may terminate this Agreement with 30 days written notice. The Company may terminate immediately for cause, including but not limited to breach of confidentiality or violation of company policies.",
                "summary": "This clause defines termination procedures and conditions for immediate termination.",
                "risk_level": "High",
                "entities": ["Time: 30 days"],
                "word_count": 35
            },
            {
                "clause_id": "clause_5",
                "original_text": "For a period of one year following termination, the Employee shall not work for any competing company within a 50-mile radius of the Company's headquarters.",
                "summary": "This clause establishes a non-compete restriction with specific geographic and time limitations.",
                "risk_level": "High",
                "entities": ["Time: 1 year", "Distance: 50 miles"],
                "word_count": 30
            }
        ],
        "risk_summary": {"High": 3, "Medium": 0, "Low": 2},
        "total_clauses": 5,
        "upload_time": datetime.now().isoformat()
    }
}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Mock Legal Document Analysis API",
        "version": "1.0.0",
        "status": "running",
        "note": "This is a mock API for testing and demo purposes"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(mock_documents),
        "mock_mode": True
    }

@app.post("/upload")
async def upload_document():
    """Mock document upload."""
    doc_id = str(uuid.uuid4())
    
    # Return a mock response
    return {
        "doc_id": doc_id,
        "filename": "sample_contract.pdf",
        "message": "Document processed successfully (mock mode)",
        "clauses_count": 5,
        "risk_summary": {"High": 3, "Medium": 0, "Low": 2},
        "ai_analysis": True,
        "mock_mode": True
    }

@app.get("/clauses/{doc_id}")
async def get_clauses(doc_id: str):
    """Get clauses for a document."""
    if doc_id in mock_documents:
        return mock_documents[doc_id]
    elif doc_id == "demo-doc-1":
        return mock_documents["demo-doc-1"]
    else:
        # Return demo data for any doc_id
        return mock_documents["demo-doc-1"]

@app.post("/ask")
async def ask_question(request: dict):
    """Mock Q&A functionality."""
    question = request.get("question", "")
    doc_id = request.get("doc_id", "")
    
    # Mock responses based on question keywords
    if "termination" in question.lower() or "terminate" in question.lower():
        return {
            "answer": "Based on clause_4, termination requires 30 days written notice. The Company may terminate immediately for cause, including breach of confidentiality or violation of company policies.",
            "relevant_clauses": ["clause_4"],
            "ai_processed": True,
            "mock_mode": True
        }
    elif "salary" in question.lower() or "compensation" in question.lower() or "pay" in question.lower():
        return {
            "answer": "Based on clause_2, the employee receives a base salary of $75,000 per year, payable according to the Company's regular payroll practices.",
            "relevant_clauses": ["clause_2"],
            "ai_processed": True,
            "mock_mode": True
        }
    elif "confidentiality" in question.lower() or "confidential" in question.lower():
        return {
            "answer": "Based on clause_3, the employee must maintain confidentiality of all proprietary information and trade secrets. This obligation continues after employment termination.",
            "relevant_clauses": ["clause_3"],
            "ai_processed": True,
            "mock_mode": True
        }
    elif "non-compete" in question.lower() or "compete" in question.lower():
        return {
            "answer": "Based on clause_5, there's a one-year non-compete restriction preventing work for competing companies within 50 miles of headquarters.",
            "relevant_clauses": ["clause_5"],
            "ai_processed": True,
            "mock_mode": True
        }
    else:
        return {
            "answer": "Based on the available clauses, I can help you understand various aspects of this employment agreement. Please ask about specific topics like termination, salary, confidentiality, or non-compete clauses.",
            "relevant_clauses": ["clause_1", "clause_2", "clause_3", "clause_4", "clause_5"],
            "ai_processed": True,
            "mock_mode": True
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mock Legal Document Analysis API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("🎭 Running in MOCK MODE for testing and demo")
    uvicorn.run(app, host="0.0.0.0", port=8000)
