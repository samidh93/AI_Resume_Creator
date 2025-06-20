#!/usr/bin/env python3
"""
Test script for the AI Resume Creator API
Tests the /generate-resume endpoint with real data
"""

import requests
import json
import time
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:3000"
GENERATE_RESUME_URL = f"{API_BASE_URL}/generate-resume"
HEALTH_URL = f"{API_BASE_URL}/health"

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_generate_resume():
    """Test resume generation with resume file and job description"""
    print("\n" + "="*50)
    print("Testing resume generation with job data...")
    
    resume_file_path = Path(Path(__file__).parent.parent / "input" / "sami_dhiab_resume.yaml")
    
    if not resume_file_path.exists():
        print(f"Resume file not found: {resume_file_path}")
        return False
    
    try:
        with open(resume_file_path, 'rb') as f:
            files = {'resume_file': (resume_file_path.name, f, 'application/x-yaml')}
            data = {
                'language': 'en',
                'job_data': json.dumps({
                    'job_id': '123',
                    'job_title': 'Senior System Engineer',
                    'job_description': """

                    """,
                    'company_name': 'Expleo'
                })
            }
            
            print("Sending request...")
            response = requests.post(GENERATE_RESUME_URL, files=files, data=data, timeout=60)
            
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! PDF generated at: {result.get('pdf_path')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Resume Creator API Tests")
    print("="*50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test health endpoint first
    if not test_health_endpoint():
        print("❌ Server is not running. Please start the server first.")
        return
    
    print("✅ Server is running!")
    
    # Run tests
    tests = [
        ("Resume generation (with job data)", test_generate_resume)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            #break
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 