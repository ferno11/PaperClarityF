from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import os
import shutil
from backend.utils import extract_text, split_clauses, summarize_clause, classify_risk
from backend.qa import build_embeddings, semantic_search, generate_answer

app = FastAPI(title="Legal Document Analysis API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage
documents = {}

@app.get("/")
async def root():
    """
    Root endpoint that provides API information and redirects to documentation.
    """
    return {
        "message": "Welcome to the Legal Document Analysis API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /upload": "Upload a legal document for analysis",
            "GET /clauses/{doc_id}": "Get clauses for a specific document",
            "POST /ask": "Ask questions about a document"
        }
    }

@app.get("/api")
async def redirect_to_docs():
    """
    Redirect to API documentation
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

class QuestionRequest(BaseModel):
    doc_id: str
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a legal document (PDF/DOCX), extract text, split into clauses,
    summarize each clause, and classify risk level.
    """
    try:
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save the uploaded file temporarily
        file_location = f"temp/temp_{file.filename}"
        with open(file_location, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Extract text from the document
        text = extract_text(file_location)
        if not text or len(text.strip()) < 10:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not extract text from document. Please check file format.")
        
        # Split text into clauses
        clauses = split_clauses(text)
        if not clauses:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail="Could not identify clauses in the document.")
        
        # Process each clause
        processed_clauses = []
        risk_summary = {"High": 0, "Medium": 0, "Low": 0}
        
        for i, clause_text in enumerate(clauses):
            clause_id = f"clause_{i+1}"
            summary = summarize_clause(clause_text)
            risk = classify_risk(clause_text)
            
            # Update risk summary
            risk_summary[risk] += 1
            
            # Store clause data
            clause_data = {
                "clause_id": clause_id,
                "original_text": clause_text,
                "summary": summary,
                "risk_level": risk
            }
            processed_clauses.append(clause_data)
        
        # Generate embeddings for all clauses
        embeddings = build_embeddings(clauses)
        
        # Store embeddings with clause data
        for i, clause_data in enumerate(processed_clauses):
            clause_data["embedding"] = embeddings[i].tolist() if embeddings and i < len(embeddings) else None
        
        # Store document data
        documents[doc_id] = {
            "clauses": processed_clauses,
            "risk_summary": risk_summary
        }
        
        # Clean up temporary file
        def cleanup_temp_file():
            try:
                if os.path.exists(file_location):
                    os.remove(file_location)
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")
                
        # Add cleanup to background tasks if available, otherwise do it immediately
        if background_tasks:
            background_tasks.add_task(cleanup_temp_file)
        else:
            cleanup_temp_file()
        
        return {"doc_id": doc_id, "message": "Document processed successfully", "clauses_count": len(processed_clauses)}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up on error
        try:
            if os.path.exists(file_location):
                os.remove(file_location)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/clauses/{doc_id}")
async def get_clauses(doc_id: str):
    """
    Retrieve all clauses for a specific document.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Return clauses without embeddings
    clauses = []
    for clause in documents[doc_id]["clauses"]:
        clauses.append({
            "clause_id": clause["clause_id"],
            "original_text": clause["original_text"],
            "summary": clause["summary"],
            "risk_level": clause["risk_level"]
        })
    
    return {
        "doc_id": doc_id,
        "clauses": clauses,
        "risk_summary": documents[doc_id]["risk_summary"],
        "total_clauses": len(clauses)
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Answer a question about a specific document by retrieving relevant clauses
    and generating an answer using an LLM.
    """
    doc_id = request.doc_id
    question = request.question
    
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question is too short or empty")
    
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all clauses and their embeddings
    clauses = documents[doc_id]["clauses"]
    clause_texts = [clause["original_text"] for clause in clauses]
    embeddings = [clause.get("embedding") for clause in clauses]
    
    # Find relevant clauses using semantic search
    try:
        relevant_indices = semantic_search(question, embeddings)
        relevant_clauses = [clauses[i] for i in relevant_indices if i < len(clauses)]
        
        if not relevant_clauses:
            return {
                "answer": "I couldn't find relevant clauses to answer your question. Please try rephrasing your question.",
                "relevant_clauses": []
            }
        
        # Generate answer using LLM
        answer = generate_answer(question, relevant_clauses)
        
        # Return answer with references to relevant clauses
        return {
            "answer": answer,
            "relevant_clauses": [clause["clause_id"] for clause in relevant_clauses]
        }
    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing your question")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)