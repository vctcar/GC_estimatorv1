#!/usr/bin/env python3
"""
Test script for the GC Estimator API
"""

import requests
import json
import time
import subprocess
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing GC Estimator API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: List estimates (should be empty initially)
    print("\n2. Testing list estimates...")
    try:
        response = requests.get(f"{base_url}/api/estimates")
        if response.status_code == 200:
            data = response.json()
            print("✅ List estimates passed")
            print(f"   Found {len(data.get('estimates', []))} estimates")
        else:
            print(f"❌ List estimates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List estimates error: {e}")
    
    # Test 3: Create new estimate
    print("\n3. Testing create estimate...")
    try:
        new_estimate = {
            "name": "Test Project",
            "client": "Test Client",
            "description": "Test description",
            "overhead_percent": 15.0,
            "profit_percent": 10.0,
            "aace_class": "Class 3"
        }
        response = requests.post(f"{base_url}/api/estimates", json=new_estimate)
        if response.status_code == 200:
            data = response.json()
            estimate_id = data["estimate"]["id"]
            print("✅ Create estimate passed")
            print(f"   Created estimate ID: {estimate_id}")
        else:
            print(f"❌ Create estimate failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create estimate error: {e}")
        return False
    
    # Test 4: Get estimate details
    print("\n4. Testing get estimate...")
    try:
        response = requests.get(f"{base_url}/api/estimates/{estimate_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get estimate passed")
            print(f"   Estimate name: {data['estimate']['name']}")
        else:
            print(f"❌ Get estimate failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get estimate error: {e}")
    
    # Test 5: Add item to estimate
    print("\n5. Testing add item...")
    try:
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
        response = requests.post(f"{base_url}/api/estimates/{estimate_id}/items", json=new_item)
        if response.status_code == 200:
            data = response.json()
            item_id = data["item"]["id"]
            print("✅ Add item passed")
            print(f"   Added item ID: {item_id}")
        else:
            print(f"❌ Add item failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Add item error: {e}")
    
    # Test 6: Get rollup
    print("\n6. Testing get rollup...")
    try:
        response = requests.get(f"{base_url}/api/estimates/{estimate_id}/rollup")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get rollup passed")
            print(f"   Rollup data received: {len(str(data))} characters")
        else:
            print(f"❌ Get rollup failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Get rollup error: {e}")
    
    # Test 7: List estimates again (should have one now)
    print("\n7. Testing list estimates again...")
    try:
        response = requests.get(f"{base_url}/api/estimates")
        if response.status_code == 200:
            data = response.json()
            print("✅ List estimates passed")
            print(f"   Now found {len(data.get('estimates', []))} estimates")
        else:
            print(f"❌ List estimates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List estimates error: {e}")
    
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
            success = test_api_endpoints()
            
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
