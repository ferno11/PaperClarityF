#!/usr/bin/env python3
"""
Complete System Test for Legal AI Platform
Tests all endpoints and functionality
"""

import requests
import json
import time
import os
from pathlib import Path

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend Health Check: PASSED")
            print(f"   Status: {data['status']}")
            print(f"   Auto-delete: {data['auto_delete_enabled']}")
            return True
        else:
            print(f"❌ Backend Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend Health Check: ERROR - {e}")
        return False

def test_frontend_health():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend Health Check: PASSED")
            return True
        else:
            print(f"❌ Frontend Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend Health Check: ERROR - {e}")
        return False

def test_upload_endpoint():
    """Test document upload"""
    try:
        # Create a test document
        test_content = """
        This is a test legal document for analysis.
        
        Clause 1: Tenant must pay rent by the 5th of every month. Late payment will incur a 5% penalty fee.
        
        Clause 2: Either party may terminate this agreement with 30 days written notice.
        
        Clause 3: The landlord is responsible for major structural repairs and maintenance.
        
        Clause 4: All parties agree to maintain confidentiality regarding proprietary information.
        
        Clause 5: Disputes shall be resolved through binding arbitration in the jurisdiction of the property.
        """
        
        files = {'file': ('test_contract.txt', test_content, 'text/plain')}
        response = requests.post("http://localhost:8001/api/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload Test: PASSED")
            print(f"   File ID: {data['file_id']}")
            print(f"   Filename: {data['filename']}")
            return data['file_id']
        else:
            print(f"❌ Upload Test: FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload Test: ERROR - {e}")
        return None

def test_analysis_endpoint(file_id):
    """Test document analysis"""
    try:
        response = requests.post(f"http://localhost:8001/api/analyze/{file_id}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis Test: PASSED")
            print(f"   Clauses found: {data['clauses_count']}")
            return True
        else:
            print(f"❌ Analysis Test: FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis Test: ERROR - {e}")
        return False

def test_results_endpoint(file_id):
    """Test results retrieval"""
    try:
        response = requests.get(f"http://localhost:8001/api/results/{file_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Results Test: PASSED")
            print(f"   Total clauses: {data['total_clauses']}")
            print(f"   Risk summary: {data['risk_summary']}")
            return True
        else:
            print(f"❌ Results Test: FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Results Test: ERROR - {e}")
        return False

def test_chat_endpoint(file_id):
    """Test chat functionality"""
    try:
        test_questions = [
            "What are the penalty clauses?",
            "What are the termination conditions?",
            "What are the payment terms?"
        ]
        
        for question in test_questions:
            payload = {"question": question}
            response = requests.post(
                f"http://localhost:8001/api/chat/{file_id}",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat Test '{question}': PASSED")
                print(f"   Answer: {data['answer'][:100]}...")
                print(f"   References: {data['relevant_clauses']}")
            else:
                print(f"❌ Chat Test '{question}': FAILED ({response.status_code})")
                print(f"   Response: {response.text}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Chat Test: ERROR - {e}")
        return False

def main():
    """Run complete system test"""
    print("🧪 Legal AI System - Complete Test Suite")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   py backend/main.py")
        return False
    
    # Test frontend health
    frontend_ok = test_frontend_health()
    if not frontend_ok:
        print("\n⚠️  Frontend is not running. Please start it:")
        print("   cd frontend && npm run dev")
        print("   (Continuing with backend tests...)\n")
    
    # Test upload
    file_id = test_upload_endpoint()
    if not file_id:
        print("\n❌ Upload failed. Cannot continue with other tests.")
        return False
    
    # Test analysis
    if not test_analysis_endpoint(file_id):
        print("\n❌ Analysis failed. Cannot continue with other tests.")
        return False
    
    # Test results
    if not test_results_endpoint(file_id):
        print("\n❌ Results retrieval failed.")
        return False
    
    # Test chat
    if not test_chat_endpoint(file_id):
        print("\n❌ Chat functionality failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("\n✅ System is fully functional and ready for demo!")
    print("\n📋 Next Steps:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Upload a legal document")
    print("   3. View the analysis and risk assessment")
    print("   4. Try the chat functionality")
    
    if not frontend_ok:
        print("\n⚠️  Remember to start the frontend:")
        print("   cd frontend && npm run dev")
    
    return True

if __name__ == "__main__":
    main()
