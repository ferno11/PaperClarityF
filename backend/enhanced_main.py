"""
Enhanced Legal Document Analysis API with AI Integration
Provides document analysis, clause processing, and chat functionality.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import os
import shutil
import asyncio
from datetime import datetime, timedelta
import json
from backend.utils import extract_text, split_clauses, summarize_clause, classify_risk
from backend.qa import build_embeddings, semantic_search, generate_answer

app = FastAPI(title="Legal Document Analysis API", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage with metadata
documents = {}
document_metadata = {}

# Auto-delete configuration
AUTO_DELETE_HOURS = 24  # Documents auto-delete after 24 hours

class QuestionRequest(BaseModel):
    doc_id: str
    question: str

class DocumentMetadata:
    def __init__(self, doc_id: str, filename: str, upload_time: datetime):
        self.doc_id = doc_id
        self.filename = filename
        self.upload_time = upload_time
        self.last_accessed = upload_time
        self.clauses_count = 0
        self.risk_summary = {"High": 0, "Medium": 0, "Low": 0}

async def cleanup_expired_documents():
    """Background task to clean up expired documents."""
    current_time = datetime.now()
    expired_docs = []
    
    for doc_id, metadata in document_metadata.items():
        if current_time - metadata.upload_time > timedelta(hours=AUTO_DELETE_HOURS):
            expired_docs.append(doc_id)
    
    for doc_id in expired_docs:
        try:
            del documents[doc_id]
            del document_metadata[doc_id]
            print(f"🗑️ Auto-deleted expired document: {doc_id}")
        except KeyError:
            pass

@app.on_event("startup")
async def startup_event():
    """Start background cleanup task on startup."""
    asyncio.create_task(periodic_cleanup())

async def periodic_cleanup():
    """Run cleanup every hour."""
    while True:
        await asyncio.sleep(3600)  # Wait 1 hour
        await cleanup_expired_documents()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Enhanced Legal Document Analysis API",
        "version": "2.0.0",
        "features": [
            "Document upload and processing",
            "AI-powered clause analysis",
            "Risk assessment and classification",
            "Interactive Q&A chatbot",
            "Auto-delete for privacy",
            "Real-time processing"
        ],
        "documentation": "/docs",
        "endpoints": {
            "POST /upload": "Upload a legal document for analysis",
            "GET /clauses/{doc_id}": "Get clauses for a specific document",
            "POST /ask": "Ask questions about a document",
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
    Upload a legal document (PDF/DOCX), extract text, split into clauses,
    summarize each clause, and classify risk level with AI.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.docx', '.doc']:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX files.")
        
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
        text = extract_text(file_location)
        if not text or len(text.strip()) < 10:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not extract text from document. Please check file format.")
        
        # Split text into clauses
        print(f"🔍 Splitting document into clauses...")
        clauses = split_clauses(text)
        if not clauses:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not identify clauses in the document.")
        
        # Process each clause with AI
        print(f"🤖 Processing {len(clauses)} clauses with AI...")
        processed_clauses = []
        risk_summary = {"High": 0, "Medium": 0, "Low": 0}
        
        for i, clause_text in enumerate(clauses):
            clause_id = f"clause_{i+1}"
            
            # AI-powered summarization
            summary = summarize_clause(clause_text)
            
            # AI-powered risk classification
            risk = classify_risk(clause_text)
            
            # Update risk summary
            risk_summary[risk] += 1
            
            # Extract entities (simple implementation)
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
        
        # Generate embeddings for semantic search
        print("🧠 Generating embeddings for semantic search...")
        clause_texts = [clause["original_text"] for clause in processed_clauses]
        embeddings = build_embeddings(clause_texts)
        
        # Store embeddings with clause data
        for i, clause_data in enumerate(processed_clauses):
            clause_data["embedding"] = embeddings[i].tolist() if embeddings and i < len(embeddings) else None
        
        # Store document data
        documents[doc_id] = {
            "filename": file.filename,
            "clauses": processed_clauses,
            "risk_summary": risk_summary,
            "total_clauses": len(processed_clauses),
            "upload_time": datetime.now().isoformat()
        }
        
        # Store metadata for auto-delete
        document_metadata[doc_id] = DocumentMetadata(
            doc_id=doc_id,
            filename=file.filename,
            upload_time=datetime.now()
        )
        document_metadata[doc_id].clauses_count = len(processed_clauses)
        document_metadata[doc_id].risk_summary = risk_summary
        
        # Clean up temporary file
        def cleanup_temp_file():
            try:
                if os.path.exists(file_location):
                    os.remove(file_location)
                    print(f"🗑️ Cleaned up temp file: {file_location}")
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")
        
        # Add cleanup to background tasks
        if background_tasks:
            background_tasks.add_task(cleanup_temp_file)
        else:
            cleanup_temp_file()
        
        print(f"✅ Document processed successfully: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "message": "Document processed successfully with AI analysis",
            "clauses_count": len(processed_clauses),
            "risk_summary": risk_summary,
            "ai_analysis": True,
            "auto_delete_hours": AUTO_DELETE_HOURS
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
    
    # Update last accessed time
    if doc_id in document_metadata:
        document_metadata[doc_id].last_accessed = datetime.now()
    
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
    Answer a question about a specific document using AI-powered semantic search.
    """
    doc_id = request.doc_id
    question = request.question
    
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short or empty")
    
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update last accessed time
    if doc_id in document_metadata:
        document_metadata[doc_id].last_accessed = datetime.now()
    
    # Get all clauses and their embeddings
    clauses = documents[doc_id]["clauses"]
    clause_texts = [clause["original_text"] for clause in clauses]
    embeddings = [clause.get("embedding") for clause in clauses]
    
    # Find relevant clauses using AI semantic search
    try:
        print(f"🔍 Searching for relevant clauses for question: {question}")
        relevant_indices = semantic_search(question, embeddings)
        relevant_clauses = [clauses[i] for i in relevant_indices if i < len(clauses)]
        
        if not relevant_clauses:
            return {
                "answer": "I couldn't find relevant clauses to answer your question. Please try rephrasing your question or asking about specific terms in the document.",
                "relevant_clauses": [],
                "ai_processed": True
            }
        
        # Generate AI-powered answer
        print(f"🤖 Generating AI answer based on {len(relevant_clauses)} relevant clauses...")
        answer = generate_answer(question, relevant_clauses)
        
        # Return answer with references to relevant clauses
        return {
            "answer": answer,
            "relevant_clauses": [clause["clause_id"] for clause in relevant_clauses],
            "ai_processed": True,
            "confidence": "high" if len(relevant_clauses) > 0 else "low"
        }
    except Exception as e:
        print(f"❌ Error in ask endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing your question")

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Manually delete a document and its data.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        del documents[doc_id]
        if doc_id in document_metadata:
            del document_metadata[doc_id]
        
        return {
            "message": f"Document {doc_id} deleted successfully",
            "doc_id": doc_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/documents")
async def list_documents():
    """
    List all documents with metadata (for debugging).
    """
    doc_list = []
    for doc_id, metadata in document_metadata.items():
        doc_list.append({
            "doc_id": doc_id,
            "filename": metadata.filename,
            "upload_time": metadata.upload_time.isoformat(),
            "last_accessed": metadata.last_accessed.isoformat(),
            "clauses_count": metadata.clauses_count,
            "risk_summary": metadata.risk_summary
        })
    
    return {
        "documents": doc_list,
        "total_documents": len(doc_list),
        "auto_delete_hours": AUTO_DELETE_HOURS
    }

def extract_entities_simple(text: str) -> List[str]:
    """Extract key entities from text."""
    import re
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced Legal Document Analysis API...")
    print("🤖 AI-powered risk analysis and Q&A")
    print("🔒 Auto-delete enabled for privacy")
    print("📚 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
