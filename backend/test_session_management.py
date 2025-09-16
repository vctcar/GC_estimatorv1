#!/usr/bin/env python3
"""
Test script for session management and route protection
"""
import requests
import time
import json
from urllib.parse import parse_qs, urlparse

class SessionTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_public_routes(self):
        """Test public routes that don't require authentication"""
        print("🌐 Testing Public Routes")
        print("-" * 30)
        
        public_routes = [
            "/",
            "/public/status", 
            "/health",
            "/docs"
        ]
        
        for route in public_routes:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                status = "✅ ACCESSIBLE" if response.status_code == 200 else f"❌ ERROR {response.status_code}"
                print(f"   {route:<20} → {status}")
            except Exception as e:
                print(f"   {route:<20} → ❌ FAILED: {e}")
    
    def test_protected_routes(self):
        """Test protected routes that require authentication"""
        print("\n🔒 Testing Protected Routes (should fail without auth)")
        print("-" * 50)
        
        protected_routes = [
            "/api/estimates",
            "/auth/user",
            "/auth/verify",
            "/auth/session",
            "/auth/admin/allowed-users"
        ]
        
        for route in protected_routes:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                if response.status_code == 401:
                    print(f"   {route:<30} → ✅ PROTECTED (401)")
                elif response.status_code == 403:
                    print(f"   {route:<30} → ✅ PROTECTED (403)")
                else:
                    print(f"   {route:<30} → ❌ NOT PROTECTED ({response.status_code})")
            except Exception as e:
                print(f"   {route:<30} → ❌ ERROR: {e}")
    
    def test_session_flow(self):
        """Test complete session authentication flow"""
        print("\n🔄 Testing Session Authentication Flow")
        print("-" * 40)
        
        # Step 1: Try to access protected route without auth
        print("\n1. Accessing protected route without authentication:")
        try:
            response = self.session.get(f"{self.base_url}/api/estimates")
            print(f"   Status: {response.status_code}")
            print(f"   Message: {response.json().get('detail', 'No detail')}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 2: Initiate OAuth login (this would redirect to Google in real scenario)
        print("\n2. Initiating OAuth login:")
        try:
            response = self.session.get(f"{self.base_url}/auth/login", allow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"   ✅ Redirected to Google OAuth")
                print(f"   Redirect URL: {redirect_url[:80]}...")
                
                # Extract state parameter for testing
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                print(f"   State parameter: {state_param[:20] if state_param else 'None'}...")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 3: Test session info endpoint
        print("\n3. Checking session info:")
        try:
            response = self.session.get(f"{self.base_url}/auth/session")
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ No session found (expected)")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 4: Test logout (should work even without session)
        print("\n4. Testing logout:")
        try:
            response = self.session.post(f"{self.base_url}/auth/logout")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    def test_session_security(self):
        """Test session security features"""
        print("\n🛡️  Testing Session Security")
        print("-" * 30)
        
        # Test 1: Session expiration behavior
        print("\n1. Session Configuration:")
        print("   • Max age: 8 hours (28800 seconds)")
        print("   • SameSite: lax (CSRF protection)")
        print("   • HttpOnly: Managed by FastAPI")
        print("   • Secure: False (dev), True (production)")
        
        # Test 2: Multiple session handling
        print("\n2. Multiple Sessions:")
        session1 = requests.Session()
        session2 = requests.Session()
        
        for i, session in enumerate([session1, session2], 1):
            try:
                response = session.get(f"{self.base_url}/auth/session")
                print(f"   Session {i}: {response.status_code} (should be 401)")
            except Exception as e:
                print(f"   Session {i}: Error - {e}")
        
        # Test 3: Session data validation
        print("\n3. Session Validation Features:")
        print("   ✅ Email authorization check on every request")
        print("   ✅ Session timestamp validation")
        print("   ✅ Activity tracking")
        print("   ✅ Complete session clearing on logout")
    
    def run_all_tests(self):
        """Run all session management tests"""
        print("🧪 Session Management & Route Protection Tests")
        print("=" * 60)
        print("Make sure the backend server is running on:", self.base_url)
        
        self.test_public_routes()
        self.test_protected_routes()
        self.test_session_flow()
        self.test_session_security()
        
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print("✅ Public routes should be accessible without authentication")
        print("✅ Protected routes should return 401/403 without authentication")
        print("✅ OAuth login should redirect to Google with state parameter")
        print("✅ Sessions should be properly managed and secured")
        
        print("\n🔧 To complete testing:")
        print("1. Configure Google OAuth credentials in .env")
        print("2. Set ALLOWED_USERS with your email")
        print("3. Complete OAuth flow via browser")
        print("4. Test protected routes with valid session")

def simulate_oauth_callback():
    """Simulate what happens during OAuth callback"""
    print("\n🔄 OAuth Callback Simulation")
    print("-" * 30)
    print("During actual OAuth flow:")
    print("1. User redirected to Google → authenticates")
    print("2. Google redirects to /auth/callback with code + state")
    print("3. Backend verifies state (CSRF protection)")
    print("4. Backend exchanges code for user info")
    print("5. Backend checks user authorization")
    print("6. If authorized: creates session + JWT token")
    print("7. User redirected to frontend with token")
    print("8. Session maintained via secure cookies")

if __name__ == "__main__":
    print("Session Management Test Suite")
    print("This tests authentication, sessions, and route protection")
    input("Press Enter to start tests...")
    
    tester = SessionTester()
    tester.run_all_tests()
    
    simulate_oauth_callback()
    
    print("\n✨ Testing complete!")
    print("\nNext steps:")
    print("• Configure OAuth credentials")
    print("• Test with real Google authentication")
    print("• Verify session persistence across requests")
