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
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import logging
try:
    from sentence_transformers import SentenceTransformer, util
except Exception as _e:
    # sentence-transformers is an optional dependency for semantic search.
    # Fall back gracefully so the API can run without it (uses mock search).
    SentenceTransformer = None
    util = None

app = FastAPI(title="Legal Document Analysis API", version="1.0.0")

# Simple module logger
logger = logging.getLogger("genai_legal")
logging.basicConfig(level=logging.INFO)
from .gemini_adapter import is_configured as gemini_configured, generate_answer_gemini

# Lightweight request logging middleware to help diagnose client errors like "Failed to fetch"
@app.middleware("http")
async def log_requests(request, call_next):
    try:
        client = request.client.host if request.client else 'unknown'
    except Exception:
        client = 'unknown'
    content_length = request.headers.get('content-length', 'unknown')
    logger.info(f"Incoming request from {client}: {request.method} {request.url.path} (Content-Length: {content_length})")
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Error while handling {request.method} {request.url.path}: {e}")
        raise
    duration = time.time() - start
    logger.info(f"Responded {request.method} {request.url.path} -> {getattr(response, 'status_code', 'unknown')} in {duration:.3f}s")
    return response

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

# Load embeddings model once (lightweight model for fast inference)
embedder = None
if SentenceTransformer is not None:
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("Semantic search model loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load semantic search model: {e}")
        embedder = None
else:
    print("Warning: sentence-transformers not available; semantic search disabled")

class QuestionRequest(BaseModel):
    # Legacy request model for /ask kept for backward compatibility
    question: str
    # Doc id is required for the legacy endpoint which used to accept both
    # a question and the document id to query against.
    doc_id: str

class ChatQuery(BaseModel):
    question: str

# Mock AI functions - replace with real implementations later
def extract_text(file_path: str) -> str:
    """Mock text extraction - replace with real PDF/DOCX extraction."""
    return """
    This is a sample legal document for testing purposes.
    
    Clause 1: Tenant must pay rent by the 5th of every month. Late payment will incur a 5% penalty fee.
    
    Clause 2: Either party may terminate this agreement with 30 days written notice.
    
    Clause 3: The landlord is responsible for major structural repairs and maintenance.
    
    Clause 4: All parties agree to maintain confidentiality regarding proprietary information.
    
    Clause 5: Disputes shall be resolved through binding arbitration in the jurisdiction of the property.
    """

def split_clauses(text: str) -> List[str]:
    """Mock clause splitting - replace with real NLP processing."""
    # Simple split by "Clause X:" pattern
    import re
    clauses = re.split(r'Clause \d+:', text)
    return [clause.strip() for clause in clauses if clause.strip()]

def summarize_clause(clause: str) -> str:
    """Mock summarization - replace with real LLM."""
    if len(clause) > 100:
        return clause[:100] + "..."
    return clause

def classify_risk(clause: str) -> str:
    """Enhanced risk classification with better heuristics."""
    clause_lower = clause.lower()
    
    # High risk indicators
    high_risk_keywords = [
        'penalty', 'fine', 'termination', 'breach', 'default', 'dispute', 'arbitration',
        'liability', 'damages', 'indemnify', 'warranty', 'guarantee', 'forfeit',
        'liquidated damages', 'consequential damages', 'punitive', 'criminal',
        'prosecution', 'lawsuit', 'litigation', 'court', 'judgment', 'enforce',
        'irrevocable', 'binding', 'mandatory', 'required', 'must', 'shall not',
        'prohibited', 'forbidden', 'illegal', 'unlawful', 'violation'
    ]
    
    # Medium risk indicators
    medium_risk_keywords = [
        'notice', 'payment', 'maintenance', 'repair', 'renewal', 'extension',
        'modification', 'amendment', 'change', 'update', 'revise', 'alter',
        'schedule', 'timeline', 'deadline', 'due date', 'expiration', 'expire',
        'renew', 'extend', 'continue', 'ongoing', 'permanent', 'temporary',
        'condition', 'requirement', 'obligation', 'responsibility', 'duty',
        'comply', 'adhere', 'follow', 'observe', 'respect', 'honor'
    ]
    
    # Low risk indicators
    low_risk_keywords = [
        'information', 'data', 'record', 'document', 'file', 'copy', 'duplicate',
        'reference', 'example', 'sample', 'template', 'format', 'structure',
        'description', 'explanation', 'clarification', 'definition', 'meaning',
        'purpose', 'objective', 'goal', 'aim', 'intent', 'intention', 'scope',
        'coverage', 'inclusion', 'exclusion', 'exception', 'special', 'particular'
    ]
    
    # Count keyword matches
    high_count = sum(1 for keyword in high_risk_keywords if keyword in clause_lower)
    medium_count = sum(1 for keyword in medium_risk_keywords if keyword in clause_lower)
    low_count = sum(1 for keyword in low_risk_keywords if keyword in clause_lower)
    
    # Additional heuristics
    has_penalty_language = any(phrase in clause_lower for phrase in [
        'penalty of', 'fine of', 'charge of', 'cost of', 'fee of', 'amount of'
    ])
    
    has_legal_action = any(phrase in clause_lower for phrase in [
        'legal action', 'court action', 'sue', 'sued', 'lawsuit', 'litigation'
    ])
    
    has_time_pressure = any(phrase in clause_lower for phrase in [
        'immediately', 'urgent', 'asap', 'within 24 hours', 'within 48 hours',
        'without delay', 'promptly', 'expeditiously'
    ])
    
    # Scoring system
    risk_score = 0
    
    # Base keyword scoring
    risk_score += high_count * 3
    risk_score += medium_count * 2
    risk_score += low_count * 1
    
    # Additional risk factors
    if has_penalty_language:
        risk_score += 5
    if has_legal_action:
        risk_score += 8
    if has_time_pressure:
        risk_score += 3
    
    # Length and complexity factors
    if len(clause.split()) > 50:  # Very long clauses are often complex
        risk_score += 2
    
    if any(char in clause for char in [';', ':', '(', ')', '[', ']']):  # Complex punctuation
        risk_score += 1
    
    # Determine risk level
    if risk_score >= 8:
        return "High"
    elif risk_score >= 4:
        return "Medium"
    else:
        return "Low"

def build_embeddings(texts: List[str]) -> List[List[float]]:
    """Mock embeddings - replace with real vector embeddings."""
    import random
    return [[random.random() for _ in range(10)] for _ in texts]

def semantic_search(query: str, embeddings: List[List[float]]) -> List[int]:
    """Mock semantic search - replace with real vector search."""
    # Return all indices for now
    return list(range(len(embeddings)))

def generate_answer(question: str, relevant_clauses: List[Dict[str, Any]]) -> str:
    """Mock answer generation - replace with real LLM."""
    context = "\n".join([f"Clause {i+1}: {clause['original_text']}" for i, clause in enumerate(relevant_clauses)])
    return f"Based on the document analysis, here's what I found regarding '{question}':\n\n{context[:200]}..."

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

async def delete_file_later(file_path: str, file_id: str, delay: int = 86400):
    """Background task to delete file after specified delay (24 hours default)."""
    print(f"Scheduling deletion of {file_path} and file_id {file_id} in {delay} seconds.")
    await asyncio.sleep(delay)
    
    # Delete file
    if os.path.exists(file_path):
        os.remove(file_path)
    print(f"Deleted file: {file_path}")
    
    # Delete results file
    results_file = os.path.join(RESULTS_DIR, f"{file_id}_results.json")
    if os.path.exists(results_file):
        os.remove(results_file)
    print(f"Deleted results: {results_file}")
    
    # Remove from memory
    if file_id in documents:
        del documents[file_id]
    print(f"Removed document {file_id} from memory")
    
    if file_id in file_metadata:
        del file_metadata[file_id]
    print(f"Removed metadata for {file_id}")

async def cleanup_expired_files():
    """Background task to clean up expired files periodically."""
    while True:
        try:
            now = datetime.utcnow()
            expired_files = []
            
            # Check file metadata for expired files
            for file_id, metadata in list(file_metadata.items()):
                upload_time = datetime.fromisoformat(metadata.get("upload_time", now.isoformat()))
                if now - upload_time > timedelta(hours=AUTO_DELETE_HOURS):
                    expired_files.append(file_id)
            
            # Clean up expired files
            for file_id in expired_files:
                await delete_file_later("", file_id, 0)  # Immediate deletion
            
            if expired_files:
                print(f"🧹 Cleaned up {len(expired_files)} expired files")
            
        except Exception as e:
            print(f"❌ Error in cleanup task: {e}")
        
        # Run cleanup every hour
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    """Start background cleanup task on startup."""
    asyncio.create_task(cleanup_expired_files())
    print("🚀 Auto-delete cleanup task started")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Legal Document Analysis API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /api/upload": "Upload a legal document for analysis",
            "POST /api/analyze/{file_id}": "Trigger analysis for an uploaded document",
            "GET /api/results/{file_id}": "Get full analysis results for a document",
            "POST /api/chat/{file_id}": "Chat with the document",
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

@app.post("/api/upload")
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

@app.post("/api/analyze/{file_id}")
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
                "embedding": clause_embeddings[i] if clause_embeddings and i < len(clause_embeddings) else None
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

@app.get("/api/results/{file_id}")
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

@app.post("/api/chat/{file_id}")
async def chat_with_doc(file_id: str, query: ChatQuery):
    """
    Answer a question about a specific document using semantic search and AI.
    """
    results = load_results(file_id)
    if not results:
        raise HTTPException(status_code=404, detail="No analysis available. Please analyze the document first.")
    
    question = query.question
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short or empty")
    
    try:
        clauses = results["clauses"]
        if not clauses:
            return {
                "answer": "⚠️ No clauses found in this document.",
                "relevant_clauses": []
            }

        # Prepare clause data for semantic search
        clause_texts = [clause["original_text"] for clause in clauses]
        clause_ids = [clause["clause_id"] for clause in clauses]

        # Try semantic search but guard it with a timeout and run blocking work in a thread
        relevant_clauses = []
        relevant_ids = []
        if embedder is not None:
            def _semantic_search_sync(question, clause_texts, clause_ids):
                try:
                    question_embedding = embedder.encode([question], convert_to_tensor=True)
                    clause_embeddings = embedder.encode(clause_texts, convert_to_tensor=True)

                    similarities = util.cos_sim(question_embedding, clause_embeddings)[0]
                    top_k = min(3, len(clause_texts))
                    topk = similarities.topk(k=top_k)
                    top_indices = topk.indices.tolist()
                    top_scores = topk.values.tolist()

                    found_ids = []
                    for idx, score in zip(top_indices, top_scores):
                        if score and float(score) > 0.3:
                            found_ids.append(clause_ids[idx])

                    return found_ids
                except Exception as e:
                    logger.exception(f"Semantic search error: {e}")
                    return []

            try:
                # Limit semantic search to 10 seconds to avoid long blocking operations
                found_ids = await asyncio.wait_for(
                    asyncio.to_thread(_semantic_search_sync, question, clause_texts, clause_ids),
                    timeout=10.0
                )
                if found_ids:
                    logger.info("chat_with_doc: semantic search returned results")
                    relevant_ids = found_ids
                    # Map ids to full clause objects
                    relevant_clauses = [c for c in clauses if c.get("clause_id") in relevant_ids]
                else:
                    logger.info("chat_with_doc: semantic search returned no results, falling back to keyword search")
            except asyncio.TimeoutError:
                logger.warning("chat_with_doc: semantic search timed out after 10s, falling back to keyword search")
            except Exception as e:
                logger.exception(f"chat_with_doc: unexpected error during semantic search: {e}")
        
    # If semantic search did not populate relevant_clauses, run simple keyword overlap
        if not relevant_clauses:
            question_lower = question.lower()
            relevant_clauses = []
            relevant_ids = []
            for i, clause_text in enumerate(clause_texts):
                clause_lower = clause_text.lower()
                question_words = set(question_lower.split())
                clause_words = set(clause_lower.split())
                common_words = question_words.intersection(clause_words)
                if len(common_words) >= 2:
                    relevant_clauses.append(clauses[i])
                    relevant_ids.append(clause_ids[i])

        if not relevant_clauses:
            return {
                "answer": "⚠️ Sorry, I couldn't find any clauses relevant to your question. Please try rephrasing or asking about different aspects of the document.",
                "relevant_clauses": []
            }

        # If Gemini is configured, try to generate a high-quality answer from the relevant clauses
        if gemini_configured():
            try:
                gemini_answer = generate_answer_gemini(question, relevant_clauses)
                if gemini_answer:
                    return {"answer": gemini_answer, "relevant_clauses": [c.get("clause_id") for c in relevant_clauses]}
            except Exception:
                logger.exception("Gemini adapter failed; falling back to local summarization")

        # Local summarization fallback
        answer_parts = []
        for c in relevant_clauses[:3]:
            clause_text = c.get('original_text', '')
            summary = clause_text[:200] + "..." if len(clause_text) > 200 else clause_text
            answer_parts.append(f"• {summary}")

        answer = f"Based on the document analysis:\n\n" + "\n\n".join(answer_parts)

        return {
            "answer": answer,
            "relevant_clauses": [c.get("clause_id") for c in relevant_clauses[:3]]
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing your question. Please try again.")

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
    print("Starting Legal Document Analysis API...")
    print("API Documentation: http://localhost:9000/docs")
    print("Auto-delete enabled for privacy (24 hours)")
    uvicorn.run(app, host="0.0.0.0", port=9000)