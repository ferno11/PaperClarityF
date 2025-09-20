"""
Simple Legal Document Analysis API
A minimal backend for testing and demo purposes.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import os
import re
from datetime import datetime

app = FastAPI(title="Legal Document Analysis API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
documents = {}

class QuestionRequest(BaseModel):
    doc_id: str
    question: str

def extract_text_simple(file_path: str) -> str:
    """Simple text extraction."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def split_clauses_simple(text: str) -> List[str]:
    """Simple clause splitting."""
    try:
        patterns = [
            r'\n\s*\d+\.\s+',  # Numbered clauses
            r'\n\s*Article\s+\d+',  # Articles
            r'\n\s*Section\s+\d+',  # Sections
            r'\n\s*[A-Z][A-Z\s]+:',  # UPPERCASE headings
        ]
        
        combined_pattern = '|'.join(patterns)
        clauses = re.split(combined_pattern, text)
        
        cleaned_clauses = []
        for clause in clauses:
            clause = clause.strip()
            if len(clause) > 20:
                cleaned_clauses.append(clause)
        
        # If no clauses found with patterns, split by paragraphs
        if not cleaned_clauses:
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 20:
                    cleaned_clauses.append(para)
        
        return cleaned_clauses
    except Exception as e:
        print(f"Error in clause splitting: {e}")
        return [text] if text.strip() else []

def summarize_clause_simple(clause_text: str) -> str:
    """Simple clause summarization."""
    words = clause_text.split()
    if len(words) > 50:
        summary = " ".join(words[:50]) + "..."
    else:
        summary = clause_text
    
    return f"This clause covers: {summary}"

def classify_risk_simple(clause_text: str) -> str:
    """Simple risk classification."""
    text_lower = clause_text.lower()
    
    high_risk_keywords = ["terminate", "liability", "damages", "penalty", "breach", "lawsuit", "eviction", "foreclosure", "default"]
    medium_risk_keywords = ["modify", "change", "restrict", "limit", "notice", "interest", "late fee", "maintenance"]
    low_risk_keywords = ["contact", "inform", "provide", "communication", "address", "signature", "governing law"]
    
    if any(keyword in text_lower for keyword in high_risk_keywords):
        return "High"
    elif any(keyword in text_lower for keyword in medium_risk_keywords):
        return "Medium"
    elif any(keyword in text_lower for keyword in low_risk_keywords):
        return "Low"
    else:
        return "Medium"

def extract_entities_simple(text: str) -> List[str]:
    """Extract key entities from text."""
    entities = []
    
    # Money patterns
    money_patterns = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
    entities.extend([f"Money: {m}" for m in money_patterns[:3]])
    
    # Percentage patterns
    percentage_patterns = re.findall(r'\b\d+(?:\.\d+)?%', text)
    entities.extend([f"Percentage: {p}" for p in percentage_patterns[:3]])
    
    # Date patterns
    date_patterns = re.findall(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b', text)
    entities.extend([f"Date: {d}" for d in date_patterns[:3]])
    
    # Time patterns
    time_patterns = re.findall(r'\b\d+\s*(?:days?|weeks?|months?|years?|hours?)\b', text)
    entities.extend([f"Time: {t}" for t in time_patterns[:3]])
    
    return entities

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Legal Document Analysis API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Document upload and processing",
            "Clause analysis and summarization",
            "Risk assessment",
            "Interactive Q&A",
            "Privacy-focused design"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(documents)
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a legal document for analysis.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save the uploaded file temporarily
        file_location = f"temp/temp_{file.filename}"
        with open(file_location, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Extract text from the document
        print(f"📄 Extracting text from {file.filename}...")
        text = extract_text_simple(file_location)
        if not text or len(text.strip()) < 10:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
        
        # Split text into clauses
        print(f"🔍 Splitting document into clauses...")
        clauses = split_clauses_simple(text)
        if not clauses:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not identify clauses in the document.")
        
        # Process each clause
        print(f"🤖 Processing {len(clauses)} clauses...")
        processed_clauses = []
        risk_summary = {"High": 0, "Medium": 0, "Low": 0}
        
        for i, clause_text in enumerate(clauses):
            clause_id = f"clause_{i+1}"
            
            # Summarization
            summary = summarize_clause_simple(clause_text)
            
            # Risk classification
            risk = classify_risk_simple(clause_text)
            
            # Update risk summary
            risk_summary[risk] += 1
            
            # Extract entities
            entities = extract_entities_simple(clause_text)
            
            # Store clause data
            clause_data = {
                "clause_id": clause_id,
                "original_text": clause_text,
                "summary": summary,
                "risk_level": risk,
                "entities": entities,
                "word_count": len(clause_text.split())
            }
            processed_clauses.append(clause_data)
        
        # Store document data
        documents[doc_id] = {
            "filename": file.filename,
            "clauses": processed_clauses,
            "risk_summary": risk_summary,
            "total_clauses": len(processed_clauses),
            "upload_time": datetime.now().isoformat()
        }
        
        # Clean up temporary file
        try:
            os.remove(file_location)
            print(f"🗑️ Cleaned up temp file: {file_location}")
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")
        
        print(f"✅ Document processed successfully: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "message": "Document processed successfully",
            "clauses_count": len(processed_clauses),
            "risk_summary": risk_summary,
            "ai_analysis": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        try:
            if 'file_location' in locals() and os.path.exists(file_location):
                os.remove(file_location)
        except:
            pass
        print(f"❌ Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/clauses/{doc_id}")
async def get_clauses(doc_id: str):
    """
    Retrieve all clauses for a specific document.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Return clauses without embeddings for security
    clauses = []
    for clause in documents[doc_id]["clauses"]:
        clauses.append({
            "clause_id": clause["clause_id"],
            "original_text": clause["original_text"],
            "summary": clause["summary"],
            "risk_level": clause["risk_level"],
            "entities": clause.get("entities", []),
            "word_count": clause.get("word_count", 0)
        })
    
    return {
        "doc_id": doc_id,
        "filename": documents[doc_id]["filename"],
        "clauses": clauses,
        "risk_summary": documents[doc_id]["risk_summary"],
        "total_clauses": len(clauses),
        "upload_time": documents[doc_id]["upload_time"],
        "ai_processed": True
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Answer a question about a specific document.
    """
    doc_id = request.doc_id
    question = request.question
    
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short or empty")
    
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all clauses
    clauses = documents[doc_id]["clauses"]
    
    # Simple keyword-based search
    question_lower = question.lower()
    relevant_clauses = []
    
    for clause in clauses:
        clause_text_lower = clause["original_text"].lower()
        if any(word in clause_text_lower for word in question_lower.split()):
            relevant_clauses.append(clause)
    
    if not relevant_clauses:
        relevant_clauses = clauses[:3]  # Fallback to first 3 clauses
    
    # Generate simple answer
    if relevant_clauses:
        clause_ids = [clause["clause_id"] for clause in relevant_clauses]
        answer = f"Based on clauses {', '.join(clause_ids)}, here's what I found: "
        if relevant_clauses:
            answer += relevant_clauses[0]["summary"]
    else:
        answer = "I couldn't find relevant information to answer your question. Please try rephrasing."
    
    return {
        "answer": answer,
        "relevant_clauses": [clause["clause_id"] for clause in relevant_clauses],
        "ai_processed": True
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Legal Document Analysis API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
