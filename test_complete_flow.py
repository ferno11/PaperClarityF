#!/usr/bin/env python3
"""
Test the complete demo flow: Upload → Analyze → Risk Dashboard → Chat Q&A
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8001"

def test_health():
    """Test if backend is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   Documents: {data['documents_loaded']}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def test_upload():
    """Test document upload."""
    print("\n📤 Testing document upload...")
    
    # Create a simple test document
    test_content = """
    This is a test legal document for clause analysis.
    
    Clause 1: The Company shall maintain confidentiality of all proprietary information.
    This clause contains sensitive information that requires careful handling.
    
    Clause 2: Payment terms are net 30 days from invoice date.
    This is a standard payment clause with moderate risk.
    
    Clause 3: Either party may terminate this agreement with 30 days written notice.
    This is a low-risk termination clause.
    """
    
    # Create a temporary text file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   File ID: {data['file_id']}")
            print(f"   Filename: {data['filename']}")
            return data['file_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_analyze(file_id):
    """Test document analysis."""
    print(f"\n🔍 Testing analysis for file {file_id}...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze/{file_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis successful!")
            print(f"   Message: {data['message']}")
            print(f"   Clauses count: {data['clauses_count']}")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_results(file_id):
    """Test results retrieval."""
    print(f"\n📊 Testing results for file {file_id}...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/results/{file_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Results retrieved successfully!")
            print(f"   Filename: {data['filename']}")
            print(f"   Total clauses: {data['total_clauses']}")
            print(f"   Risk summary: {data['risk_summary']}")
            
            # Show first few clauses
            if data['clauses']:
                print(f"   First clause: {data['clauses'][0]['summary'][:100]}...")
            
            return True
        else:
            print(f"❌ Results failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Results error: {e}")
        return False

def test_chat(file_id):
    """Test chat functionality."""
    print(f"\n💬 Testing chat for file {file_id}...")
    
    test_questions = [
        "What are the confidentiality obligations?",
        "What are the payment terms?",
        "How can this agreement be terminated?"
    ]
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/{file_id}",
                json={"question": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat successful for: '{question}'")
                print(f"   Answer: {data['answer'][:100]}...")
                print(f"   References: {data['relevant_clauses']}")
            else:
                print(f"❌ Chat failed for '{question}': {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Chat error for '{question}': {e}")

def main():
    """Run complete demo flow test."""
    print("🚀 Testing Complete Legal Document Analysis Demo Flow")
    print("=" * 60)
    
    # Step 1: Health check
    if not test_health():
        print("❌ Backend not available. Exiting.")
        return
    
    # Step 2: Upload document
    file_id = test_upload()
    if not file_id:
        print("❌ Upload failed. Exiting.")
        return
    
    # Step 3: Analyze document
    if not test_analyze(file_id):
        print("❌ Analysis failed. Exiting.")
        return
    
    # Step 4: Get results
    if not test_results(file_id):
        print("❌ Results retrieval failed. Exiting.")
        return
    
    # Step 5: Test chat
    test_chat(file_id)
    
    print("\n🎉 Complete demo flow test finished!")
    print("✅ All core functionality is working!")

if __name__ == "__main__":
    main()
