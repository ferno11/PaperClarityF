#!/usr/bin/env python3
"""
Test script to demonstrate the GenAI Legal Tool functionality.
"""

import requests
import json

def test_backend():
    """Test the backend functionality."""
    print("🚀 GenAI Legal Tool - Backend Test")
    print("=" * 50)
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test document upload
    print("\n📄 Testing document upload...")
    try:
        with open("sample_contract.txt", "rb") as f:
            files = {"file": ("sample_contract.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload", files=files)
        
        if response.status_code == 200:
            print("✅ Document uploaded successfully!")
            data = response.json()
            print(f"   Document ID: {data['doc_id']}")
            print(f"   Filename: {data['filename']}")
            print(f"   Clauses found: {data['clauses_count']}")
            print(f"   Risk summary: {data['risk_summary']}")
            doc_id = data['doc_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test getting clauses
    print(f"\n📋 Testing clauses retrieval...")
    try:
        response = requests.get(f"http://localhost:8000/clauses/{doc_id}")
        if response.status_code == 200:
            print("✅ Clauses retrieved successfully!")
            data = response.json()
            print(f"   Total clauses: {data['total_clauses']}")
            print(f"   Risk distribution:")
            for risk, count in data['risk_summary'].items():
                print(f"     {risk}: {count}")
            
            # Show first few clauses
            print(f"\n   First 3 clauses:")
            for i, clause in enumerate(data['clauses'][:3]):
                print(f"     {i+1}. {clause['clause_id']} - {clause['risk_level']} Risk")
                print(f"        Summary: {clause['summary'][:80]}...")
        else:
            print(f"❌ Clauses retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Clauses error: {e}")
    
    # Test chat functionality
    print(f"\n💬 Testing chat functionality...")
    questions = [
        "What is the salary?",
        "What are the termination terms?",
        "What about confidentiality?"
    ]
    
    for question in questions:
        try:
            payload = {
                "doc_id": doc_id,
                "question": question
            }
            response = requests.post("http://localhost:8000/ask", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ❓ {question}")
                print(f"   🤖 {data['answer'][:100]}...")
                print(f"   📍 Relevant clauses: {data['relevant_clauses']}")
            else:
                print(f"   ❌ Chat failed for: {question}")
        except Exception as e:
            print(f"   ❌ Chat error for '{question}': {e}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Backend test completed successfully!")
    print("🌐 Frontend available at: http://localhost:3000")
    print("🔧 Backend available at: http://localhost:8000")

if __name__ == "__main__":
    test_backend()
