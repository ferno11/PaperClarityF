"""
Complete Legal Document Analysis API with all required endpoints
Implements: /upload, /analyze/{file_id}, /results/{file_id}, /chat/{file_id}
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import os
import shutil
import time
import json
from datetime import datetime, timedelta

# Import backend modules
import sys
sys.path.append('backend')
from utils import extract_text, split_clauses, summarize_clause, classify_risk
from qa import build_embeddings, semantic_search, generate_answer

app = FastAPI(title="Legal Document Analysis API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage directories
UPLOAD_DIR = "uploads/"
RESULTS_DIR = "results/"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# In-memory storage for quick access
documents: Dict[str, Dict[str, Any]] = {}
file_metadata: Dict[str, Dict[str, Any]] = {}

# Auto-delete configuration
AUTO_DELETE_HOURS = 24

class QuestionRequest(BaseModel):
    question: str

class ChatQuery(BaseModel):
    question: str

def find_file_by_id(file_id: str) -> Optional[str]:
    """Find file path by file_id."""
    if file_id in file_metadata:
        return file_metadata[file_id]["file_path"]
    return None

def save_results(file_id: str, results: Dict[str, Any]):
    """Save analysis results to disk and memory."""
    # Save to memory
    documents[file_id] = results
    
    # Save to disk
    results_file = os.path.join(RESULTS_DIR, f"{file_id}_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

def load_results(file_id: str) -> Optional[Dict[str, Any]]:
    """Load analysis results from memory or disk."""
    if file_id in documents:
        return documents[file_id]
    
    # Try to load from disk
    results_file = os.path.join(RESULTS_DIR, f"{file_id}_results.json")
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            results = json.load(f)
            documents[file_id] = results
            return results
    
    return None

def delete_file_later(file_path: str, file_id: str, delay: int = 86400):
    """Background task to delete file after specified delay (24 hours default)."""
    print(f"🗑️ Scheduling deletion of {file_path} and file_id {file_id} in {delay} seconds.")
    time.sleep(delay)
    
    # Delete file
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✅ Deleted file: {file_path}")
    
    # Delete results file
    results_file = os.path.join(RESULTS_DIR, f"{file_id}_results.json")
    if os.path.exists(results_file):
        os.remove(results_file)
        print(f"✅ Deleted results: {results_file}")
    
    # Remove from memory
    if file_id in documents:
        del documents[file_id]
        print(f"✅ Removed document {file_id} from memory")
    
    if file_id in file_metadata:
        del file_metadata[file_id]
        print(f"✅ Removed metadata for {file_id}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Legal Document Analysis API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /upload": "Upload a legal document for analysis",
            "POST /analyze/{file_id}": "Trigger analysis for an uploaded document",
            "GET /results/{file_id}": "Get full analysis results for a document",
            "POST /chat/{file_id}": "Chat with the document",
            "GET /health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(documents),
        "auto_delete_enabled": True,
        "auto_delete_hours": AUTO_DELETE_HOURS
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a legal document (PDF/DOCX) and store it temporarily.
    Analysis is triggered by a separate /analyze endpoint.
    """
    try:
        # Validate file type
        if file.content_type not in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOC, DOCX are allowed.")

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store file metadata
        file_metadata[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }

        # Schedule file for deletion after 24 hours
        if background_tasks:
            background_tasks.add_task(delete_file_later, file_path, file_id, delay=86400)
        
        return {"file_id": file_id, "filename": file.filename, "message": "Document uploaded successfully. Ready for analysis."}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/analyze/{file_id}")
async def analyze(file_id: str):
    """
    Trigger the analysis pipeline for an uploaded document.
    Uses the existing summarize_clauses.py functionality.
    """
    if file_id not in file_metadata:
        raise HTTPException(status_code=404, detail="File not found. Please upload it first.")
    
    file_info = file_metadata[file_id]
    file_path = file_info["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found on server.")

    try:
        # Update status
        file_metadata[file_id]["status"] = "processing"
        
        # Extract text
        text = extract_text(file_path)
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from document. Please check file format.")
        
        # Split text into clauses
        clauses = split_clauses(text)
        if not clauses:
            raise HTTPException(status_code=400, detail="Could not identify clauses in the document.")
        
        # Process each clause
        processed_clauses = []
        risk_summary = {"High": 0, "Medium": 0, "Low": 0}
        
        # Generate embeddings for all clauses first
        clause_embeddings = build_embeddings(clauses)

        for i, clause_text in enumerate(clauses):
            clause_id = f"clause_{i+1}"
            summary = summarize_clause(clause_text)
            risk = classify_risk(clause_text)
            
            risk_summary[risk] += 1
            
            clause_data = {
                "clause_id": clause_id,
                "original_text": clause_text,
                "summary": summary,
                "risk_level": risk,
                "word_count": len(clause_text.split()),
                "embedding": clause_embeddings[i].tolist() if clause_embeddings and i < len(clause_embeddings) else None
            }
            processed_clauses.append(clause_data)
        
        # Prepare results
        results = {
            "file_id": file_id,
            "filename": file_info["filename"],
            "clauses": processed_clauses,
            "risk_summary": risk_summary,
            "total_clauses": len(processed_clauses),
            "status": "analyzed",
            "analysis_time": datetime.now().isoformat()
        }
        
        # Save results
        save_results(file_id, results)
        
        # Update file status
        file_metadata[file_id]["status"] = "analyzed"
        
        return {"file_id": file_id, "message": "Document analyzed successfully", "clauses_count": len(processed_clauses)}
    
    except HTTPException:
        file_metadata[file_id]["status"] = "failed"
        raise
    except Exception as e:
        file_metadata[file_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")

@app.get("/results/{file_id}")
async def get_results(file_id: str):
    """
    Retrieve full analysis results for a specific document.
    """
    results = load_results(file_id)
    if not results:
        raise HTTPException(status_code=404, detail="No results found. Please analyze the document first.")
    
    # Return clauses without embeddings for lighter payload
    clauses_without_embeddings = []
    for clause in results["clauses"]:
        clause_copy = clause.copy()
        clause_copy.pop("embedding", None)  # Remove embedding before sending to frontend
        clauses_without_embeddings.append(clause_copy)

    return {
        "file_id": file_id,
        "filename": results["filename"],
        "clauses": clauses_without_embeddings,
        "risk_summary": results["risk_summary"],
        "total_clauses": results["total_clauses"],
        "status": results["status"],
        "analysis_time": results.get("analysis_time", "")
    }

@app.post("/chat/{file_id}")
async def chat_with_doc(file_id: str, query: ChatQuery):
    """
    Answer a question about a specific document using its analyzed clauses.
    """
    results = load_results(file_id)
    if not results:
        raise HTTPException(status_code=404, detail="No analysis available. Please analyze the document first.")
    
    question = query.question
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short or empty")
    
    # Get all clauses and their embeddings
    clauses = results["clauses"]
    embeddings = [clause.get("embedding") for clause in clauses]
    
    # Filter out clauses without embeddings if any
    valid_clauses_with_embeddings = [(c, e) for c, e in zip(clauses, embeddings) if e is not None]
    if not valid_clauses_with_embeddings:
        raise HTTPException(status_code=500, detail="No valid embeddings found for clauses.")

    valid_clauses = [item[0] for item in valid_clauses_with_embeddings]
    valid_embeddings = [item[1] for item in valid_clauses_with_embeddings]

    # Find relevant clauses using semantic search
    try:
        relevant_indices = semantic_search(question, valid_embeddings)
        relevant_clauses = [valid_clauses[i] for i in relevant_indices if i < len(valid_clauses)]
        
        if not relevant_clauses:
            return {
                "answer": "I couldn't find relevant clauses to answer your question. Please try rephrasing your question.",
                "relevant_clauses": []
            }
        
        # Generate answer using LLM
        answer = generate_answer(question, relevant_clauses)
        
        return {
            "answer": answer,
            "relevant_clauses": [clause["clause_id"] for clause in relevant_clauses]
        }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing your question")

# Legacy endpoints for backward compatibility
@app.get("/clauses/{doc_id}")
async def get_clauses_legacy(doc_id: str):
    """Legacy endpoint - redirects to results."""
    return await get_results(doc_id)

@app.post("/ask")
async def ask_question_legacy(request: QuestionRequest):
    """Legacy endpoint - redirects to chat."""
    return await chat_with_doc(request.doc_id, ChatQuery(question=request.question))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Legal Document Analysis API...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔒 Auto-delete enabled for privacy (24 hours)")
    uvicorn.run(app, host="0.0.0.0", port=8001)
