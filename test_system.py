#!/usr/bin/env python3
"""
Test script to verify the complete system is working
"""

import requests
import json
import time

def test_backend():
    """Test backend endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Backend...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"   Status: {response.json()['status']}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False
    
    # Test upload endpoint (with a dummy file)
    try:
        files = {'file': ('test.txt', 'This is a test document for legal analysis.', 'text/plain')}
        response = requests.post(f"{base_url}/api/upload", files=files)
        if response.status_code == 200:
            data = response.json()
            file_id = data['file_id']
            print(f"✅ File upload successful: {file_id}")
            
            # Test analysis endpoint
            response = requests.post(f"{base_url}/api/analyze/{file_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis successful: {data['clauses_count']} clauses found")
                
                # Test results endpoint
                response = requests.get(f"{base_url}/api/results/{file_id}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Results retrieval successful: {data['total_clauses']} clauses")
                    
                    # Test chat endpoint
                    chat_data = {"question": "What are the main clauses in this document?"}
                    response = requests.post(f"{base_url}/api/chat/{file_id}", json=chat_data)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Chat functionality working: {data['answer'][:100]}...")
                        return True
                    else:
                        print(f"❌ Chat test failed: {response.status_code}")
                        return False
                else:
                    print(f"❌ Results test failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Analysis test failed: {response.status_code}")
                return False
        else:
            print(f"❌ Upload test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not reachable: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Complete Legal AI System")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    if backend_ok and frontend_ok:
        print("🎉 All systems are working! You can now:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Upload a legal document")
        print("   3. View the analysis and chat with the document")
    else:
        print("❌ Some systems are not working properly")
        if not backend_ok:
            print("   - Backend issues detected")
        if not frontend_ok:
            print("   - Frontend issues detected")
