#!/usr/bin/env python3
"""
Integration Test Script for Legal AI Tool
Tests the complete frontend-backend integration.
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_DOCUMENT = "sample_contract.txt"

def test_backend_health():
    """Test if backend is running and healthy."""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data['status']}")
            print(f"   Documents loaded: {data['documents_loaded']}")
            print(f"   Auto-delete enabled: {data['auto_delete_enabled']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def test_frontend_health():
    """Test if frontend is running."""
    print("🔍 Testing frontend health...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not reachable: {e}")
        return False

def create_test_document():
    """Create a test legal document."""
    test_content = """
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into on January 1, 2024, between Company Inc. ("Company") and John Doe ("Employee").

1. TERM OF EMPLOYMENT
The Employee's employment shall commence on January 1, 2024, and shall continue until terminated in accordance with the provisions of this Agreement.

2. COMPENSATION
The Employee shall receive a base salary of $75,000 per year, payable in accordance with the Company's regular payroll practices.

3. CONFIDENTIALITY
The Employee agrees to maintain the confidentiality of all proprietary information and trade secrets of the Company. This obligation shall survive termination of employment.

4. TERMINATION
Either party may terminate this Agreement with 30 days written notice. The Company may terminate immediately for cause, including but not limited to breach of confidentiality or violation of company policies.

5. NON-COMPETE
For a period of one year following termination, the Employee shall not work for any competing company within a 50-mile radius of the Company's headquarters.

6. INDEMNIFICATION
The Employee agrees to indemnify and hold harmless the Company from any claims arising from the Employee's actions or omissions during employment.

7. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.

8. ENTIRE AGREEMENT
This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations and agreements.
"""
    
    with open(TEST_DOCUMENT, "w") as f:
        f.write(test_content)
    print(f"✅ Created test document: {TEST_DOCUMENT}")

def test_document_upload():
    """Test document upload functionality."""
    print("🔍 Testing document upload...")
    
    if not os.path.exists(TEST_DOCUMENT):
        create_test_document()
    
    try:
        with open(TEST_DOCUMENT, "rb") as f:
            files = {"file": (TEST_DOCUMENT, f, "text/plain")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document uploaded successfully")
            print(f"   Document ID: {data['doc_id']}")
            print(f"   Clauses found: {data['clauses_count']}")
            print(f"   Risk summary: {data['risk_summary']}")
            return data['doc_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_get_clauses(doc_id):
    """Test getting clauses for a document."""
    print("🔍 Testing clause retrieval...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/clauses/{doc_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clauses retrieved successfully")
            print(f"   Total clauses: {data['total_clauses']}")
            print(f"   Risk summary: {data['risk_summary']}")
            
            # Show first clause as example
            if data['clauses']:
                first_clause = data['clauses'][0]
                print(f"   First clause example:")
                print(f"     ID: {first_clause['clause_id']}")
                print(f"     Risk: {first_clause['risk_level']}")
                print(f"     Summary: {first_clause['summary'][:100]}...")
            
            return True
        else:
            print(f"❌ Clause retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Clause retrieval error: {e}")
        return False

def test_chat_functionality(doc_id):
    """Test chat functionality."""
    print("🔍 Testing chat functionality...")
    
    test_questions = [
        "What are the termination conditions?",
        "What is the salary amount?",
        "What are the confidentiality requirements?",
        "What is the non-compete period?"
    ]
    
    for question in test_questions:
        try:
            payload = {
                "doc_id": doc_id,
                "question": question
            }
            response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Question answered: '{question}'")
                print(f"   Answer: {data['answer'][:100]}...")
                print(f"   References: {data['relevant_clauses']}")
            else:
                print(f"❌ Chat failed for question: '{question}'")
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Chat error for question '{question}': {e}")

def test_privacy_features(doc_id):
    """Test privacy and auto-delete features."""
    print("🔍 Testing privacy features...")
    
    try:
        # Test document listing
        response = requests.get(f"{BACKEND_URL}/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document listing works")
            print(f"   Total documents: {data['total_documents']}")
            print(f"   Auto-delete hours: {data['auto_delete_hours']}")
        
        # Test manual deletion
        response = requests.delete(f"{BACKEND_URL}/documents/{doc_id}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Manual deletion works")
        else:
            print(f"⚠️  Manual deletion failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Privacy features error: {e}")

def run_full_test():
    """Run the complete integration test."""
    print("🚀 Starting Legal AI Integration Test")
    print("=" * 50)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("❌ Backend not available. Please start the backend first.")
        return False
    
    # Test 2: Frontend Health
    if not test_frontend_health():
        print("⚠️  Frontend not available. Backend tests will continue.")
    
    # Test 3: Document Upload
    doc_id = test_document_upload()
    if not doc_id:
        print("❌ Document upload failed. Stopping tests.")
        return False
    
    # Test 4: Get Clauses
    if not test_get_clauses(doc_id):
        print("❌ Clause retrieval failed.")
        return False
    
    # Test 5: Chat Functionality
    test_chat_functionality(doc_id)
    
    # Test 6: Privacy Features
    test_privacy_features(doc_id)
    
    # Cleanup
    if os.path.exists(TEST_DOCUMENT):
        os.remove(TEST_DOCUMENT)
        print(f"🗑️  Cleaned up test document")
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")
    print("🎯 Your Legal AI tool is ready for demo!")
    
    return True

if __name__ == "__main__":
    success = run_full_test()
    exit(0 if success else 1)
