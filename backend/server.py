#!/usr/bin/env python3
"""
GenAI Legal Tool Backend Server.
Provides document analysis, clause processing, and chat functionality.
"""

import json
import re
import uuid
import os
import tempfile
from typing import Dict, List, Any
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi
import io

# In-memory storage
documents = {}

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
        # Fallback: return the whole text as one clause
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

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy", "message": "API is running"}
            self.wfile.write(json.dumps(response).encode())
        
        elif path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "Welcome to the GenAI Legal Document Analysis API",
                "version": "1.0.0",
                "status": "running"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif path.startswith('/clauses/'):
            doc_id = path.split('/')[-1]
            if doc_id in documents:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(documents[doc_id]).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": "Document not found"}
                self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/upload':
            self.handle_upload()
        elif path == '/ask':
            self.handle_ask()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_upload(self):
        """Handle document upload using cgi."""
        try:
            # Parse multipart form data
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                fields = cgi.parse_multipart(self.rfile, pdict)
                
                # Get the file
                if 'file' in fields:
                    file_data = fields['file'][0]
                    filename = "uploaded_document.txt"  # Default filename
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    
                    # Process document
                    text = extract_text_simple(temp_file_path)
                    print(f"Extracted text length: {len(text) if text else 0}")
                    if not text or len(text.strip()) < 10:
                        os.unlink(temp_file_path)
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"error": "Could not extract text from document"}
                        self.wfile.write(json.dumps(response).encode())
                        return
                    
                    # Split into clauses
                    clauses = split_clauses_simple(text)
                    print(f"Found {len(clauses)} clauses")
                    if not clauses:
                        os.unlink(temp_file_path)
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"error": "Could not identify clauses in document"}
                        self.wfile.write(json.dumps(response).encode())
                        return
                    
                    # Process each clause
                    doc_id = str(uuid.uuid4())
                    processed_clauses = []
                    risk_summary = {"High": 0, "Medium": 0, "Low": 0}
                    
                    for i, clause_text in enumerate(clauses):
                        clause_id = f"clause_{i+1}"
                        summary = summarize_clause_simple(clause_text)
                        risk = classify_risk_simple(clause_text)
                        entities = extract_entities_simple(clause_text)
                        
                        risk_summary[risk] += 1
                        
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
                        "filename": filename,
                        "clauses": processed_clauses,
                        "risk_summary": risk_summary,
                        "total_clauses": len(processed_clauses)
                    }
                    
                    # Clean up temp file
                    os.unlink(temp_file_path)
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "doc_id": doc_id,
                        "filename": filename,
                        "message": "Document processed successfully",
                        "clauses_count": len(processed_clauses),
                        "risk_summary": risk_summary
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"error": "No file provided"}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": "Invalid content type"}
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": f"Error processing document: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_ask(self):
        """Handle chat questions."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            doc_id = data.get('doc_id')
            question = data.get('question')
            
            if not doc_id or not question:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": "Missing doc_id or question"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if doc_id not in documents:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": "Document not found"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Simple keyword-based search
            doc_data = documents[doc_id]
            clauses = doc_data["clauses"]
            
            question_lower = question.lower()
            relevant_clauses = []
            
            for clause in clauses:
                clause_text_lower = clause["original_text"].lower()
                if any(word in clause_text_lower for word in question_lower.split()):
                    relevant_clauses.append(clause)
            
            if not relevant_clauses:
                relevant_clauses = clauses[:3]
            
            # Generate simple answer
            if relevant_clauses:
                clause_ids = [clause["clause_id"] for clause in relevant_clauses]
                answer = f"Based on clauses {', '.join(clause_ids)}, here's what I found: "
                if relevant_clauses:
                    answer += relevant_clauses[0]["summary"]
            else:
                answer = "I couldn't find relevant information to answer your question. Please try rephrasing."
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "answer": answer,
                "relevant_clauses": [clause["clause_id"] for clause in relevant_clauses],
                "question": question
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": f"Error processing question: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    """Run the HTTP server."""
    server = HTTPServer(('127.0.0.1', 8000), APIHandler)
    print("🚀 GenAI Legal Tool Backend running on http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/")
    print("🔍 Health Check: http://127.0.0.1:8000/health")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
