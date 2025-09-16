#!/usr/bin/env python3
"""
Simple test script to demonstrate CSRF protection in OAuth flow
"""
import requests
import time
from urllib.parse import parse_qs, urlparse

def test_csrf_protection():
    """Test CSRF protection by simulating attack scenarios"""
    base_url = "http://localhost:8000"
    
    print("🔒 Testing CSRF Protection in OAuth Flow")
    print("=" * 50)
    
    # Test 1: Normal flow (should work)
    print("\n✅ Test 1: Normal OAuth flow")
    session = requests.Session()
    
    # Step 1: Initiate login (this stores state in session)
    login_response = session.get(f"{base_url}/auth/login", allow_redirects=False)
    print(f"Login initiated: {login_response.status_code}")
    
    if login_response.status_code == 302:
        redirect_url = login_response.headers.get('Location')
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        state_param = query_params.get('state', [None])[0]
        print(f"State parameter generated: {state_param[:10]}..." if state_param else "No state parameter")
    
    # Test 2: Callback without state (should fail)
    print("\n❌ Test 2: Callback without state parameter")
    try:
        callback_response = session.get(f"{base_url}/auth/callback", allow_redirects=False)
        print(f"Response: {callback_response.status_code} - {callback_response.text[:100]}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 3: Callback with invalid state (should fail)
    print("\n❌ Test 3: Callback with invalid state")
    try:
        callback_response = session.get(
            f"{base_url}/auth/callback?state=invalid_state_token", 
            allow_redirects=False
        )
        print(f"Response: {callback_response.status_code} - {callback_response.text[:100]}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 4: State reuse (should fail)
    print("\n❌ Test 4: State token reuse attack")
    if state_param:
        try:
            # First use
            callback_response1 = session.get(
                f"{base_url}/auth/callback?state={state_param}", 
                allow_redirects=False
            )
            print(f"First use: {callback_response1.status_code}")
            
            # Second use (should fail - single use)
            callback_response2 = session.get(
                f"{base_url}/auth/callback?state={state_param}", 
                allow_redirects=False
            )
            print(f"Reuse attempt: {callback_response2.status_code} - {callback_response2.text[:100]}")
        except Exception as e:
            print(f"Request failed: {e}")
    
    # Test 5: Cross-session attack (should fail)
    print("\n❌ Test 5: Cross-session state attack")
    
    # Create two separate sessions
    session1 = requests.Session()
    session2 = requests.Session()
    
    # Session 1 initiates login
    login1 = session1.get(f"{base_url}/auth/login", allow_redirects=False)
    if login1.status_code == 302:
        redirect_url = login1.headers.get('Location')
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        state1 = query_params.get('state', [None])[0]
        
        # Session 2 tries to use Session 1's state
        try:
            attack_response = session2.get(
                f"{base_url}/auth/callback?state={state1}", 
                allow_redirects=False
            )
            print(f"Cross-session attack: {attack_response.status_code} - {attack_response.text[:100]}")
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("\n🛡️  CSRF Protection Test Complete!")
    print("Expected results:")
    print("- Normal flow: Should redirect to Google")
    print("- All attack scenarios: Should return 400 Bad Request")

if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Start it with: python main.py")
    input("Press Enter when ready to test...")
    test_csrf_protection()
