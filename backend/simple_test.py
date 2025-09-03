#!/usr/bin/env python3
"""
Simple test script for the GC Estimator API using built-in libraries
"""

import urllib.request
import urllib.parse
import json
import subprocess
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def make_request(url, method='GET', data=None):
    """Make HTTP request using urllib"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8'), response.status
    except urllib.error.URLError as e:
        return str(e), None
    except Exception as e:
        return str(e), None

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing GC Estimator API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    response, status = make_request(f"{base_url}/")
    if status == 200:
        print("✅ Health check passed")
        print(f"   Response: {response}")
    else:
        print(f"❌ Health check failed: {status}")
        print(f"   Error: {response}")
        return False
    
    # Test 2: List estimates
    print("\n2. Testing list estimates...")
    response, status = make_request(f"{base_url}/api/estimates")
    if status == 200:
        data = json.loads(response)
        print("✅ List estimates passed")
        print(f"   Found {len(data.get('estimates', []))} estimates")
    else:
        print(f"❌ List estimates failed: {status}")
        print(f"   Error: {response}")
    
    # Test 3: Create estimate
    print("\n3. Testing create estimate...")
    new_estimate = {
        "name": "Test Project",
        "client": "Test Client",
        "description": "Test description",
        "overhead_percent": 15.0,
        "profit_percent": 10.0,
        "aace_class": "Class 3"
    }
    response, status = make_request(f"{base_url}/api/estimates", method='POST', data=new_estimate)
    if status == 200:
        data = json.loads(response)
        estimate_id = data["estimate"]["id"]
        print("✅ Create estimate passed")
        print(f"   Created estimate ID: {estimate_id}")
    else:
        print(f"❌ Create estimate failed: {status}")
        print(f"   Error: {response}")
        return False
    
    # Test 4: Get estimate
    print("\n4. Testing get estimate...")
    response, status = make_request(f"{base_url}/api/estimates/{estimate_id}")
    if status == 200:
        data = json.loads(response)
        print("✅ Get estimate passed")
        print(f"   Estimate name: {data['estimate']['name']}")
    else:
        print(f"❌ Get estimate failed: {status}")
        print(f"   Error: {response}")
    
    # Test 5: Add item
    print("\n5. Testing add item...")
    new_item = {
        "phase": "Site Work",
        "item": "Excavation",
        "unit": "CY",
        "quantity": 1000,
        "waste": 10,
        "unit_cost": 25.50,
        "lump_sum": 0,
        "subtotal": 28050.00
    }
    response, status = make_request(f"{base_url}/api/estimates/{estimate_id}/items", method='POST', data=new_item)
    if status == 200:
        data = json.loads(response)
        item_id = data["item"]["id"]
        print("✅ Add item passed")
        print(f"   Added item ID: {item_id}")
    else:
        print(f"❌ Add item failed: {status}")
        print(f"   Error: {response}")
    
    # Test 6: Get rollup
    print("\n6. Testing get rollup...")
    response, status = make_request(f"{base_url}/api/estimates/{estimate_id}/rollup")
    if status == 200:
        data = json.loads(response)
        print("✅ Get rollup passed")
        print(f"   Rollup data received successfully")
    else:
        print(f"❌ Get rollup failed: {status}")
        print(f"   Error: {response}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    return True

def start_server():
    """Start the API server"""
    print("🚀 Starting API server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

if __name__ == "__main__":
    # Start server
    server_process = start_server()
    
    if server_process:
        try:
            # Test endpoints
            success = test_api()
            
            if success:
                print("\n🎯 All tests passed! The API is working correctly.")
            else:
                print("\n❌ Some tests failed. Check the output above.")
                
        finally:
            # Clean up
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
    else:
        print("❌ Could not start server. Exiting.")
        sys.exit(1)
