#!/usr/bin/env python3
"""
Test script for home page functionality and user flow
"""
import requests
import time
from urllib.parse import parse_qs, urlparse

class HomePageTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_home_page_unauthenticated(self):
        """Test home page for unauthenticated users"""
        print("🏠 Testing Home Page (Unauthenticated)")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                print("   ✅ Home page loads successfully")
                
                # Check if it's HTML content
                if 'text/html' in response.headers.get('content-type', ''):
                    print("   ✅ Returns HTML content")
                    
                    # Check for key elements
                    content = response.text.lower()
                    checks = [
                        ("GC Estimator" in content, "Title present"),
                        ("sign in with google" in content, "Login button present"),
                        ("construction cost estimation" in content, "Project description present"),
                        ("professional" in content, "Professional branding present"),
                        ("oauth" in content, "Authentication info present")
                    ]
                    
                    for check, description in checks:
                        status = "✅" if check else "❌"
                        print(f"   {status} {description}")
                        
                else:
                    print("   ❌ Not returning HTML content")
                    
            else:
                print(f"   ❌ Home page failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing home page: {e}")
    
    def test_login_flow_initiation(self):
        """Test login flow initiation from home page"""
        print("\n🔐 Testing Login Flow Initiation")
        print("-" * 35)
        
        try:
            # Test login endpoint
            response = self.session.get(f"{self.base_url}/auth/login", allow_redirects=False)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print("   ✅ Login redirects to Google OAuth")
                
                # Parse redirect URL
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query)
                
                # Check OAuth parameters
                oauth_checks = [
                    ('client_id' in query_params, "Client ID present"),
                    ('redirect_uri' in query_params, "Redirect URI present"),
                    ('state' in query_params, "CSRF state parameter present"),
                    ('scope' in query_params, "OAuth scope present"),
                    ('response_type' in query_params, "Response type present")
                ]
                
                for check, description in oauth_checks:
                    status = "✅" if check else "❌"
                    print(f"   {status} {description}")
                
                # Show some parameter values
                if 'state' in query_params:
                    state = query_params['state'][0]
                    print(f"   📝 State parameter: {state[:20]}...")
                
                if 'redirect_uri' in query_params:
                    redirect_uri = query_params['redirect_uri'][0]
                    print(f"   📝 Redirect URI: {redirect_uri}")
                    
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing login: {e}")
    
    def test_post_login_behavior(self):
        """Test post-login behavior simulation"""
        print("\n🔄 Testing Post-Login Behavior")
        print("-" * 30)
        
        print("   📝 Post-login flow simulation:")
        print("   1. User completes Google OAuth")
        print("   2. Callback creates session + JWT token")
        print("   3. User redirected to frontend/dashboard")
        print("   4. If user visits home page again → auto-redirect")
        
        # Test dashboard endpoint without authentication
        try:
            response = self.session.get(f"{self.base_url}/dashboard", allow_redirects=False)
            
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', '')
                if redirect_location == '/':
                    print("   ✅ Unauthenticated dashboard access redirects to home")
                else:
                    print(f"   ❌ Unexpected redirect: {redirect_location}")
            else:
                print(f"   ❌ Dashboard response: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing dashboard: {e}")
    
    def test_project_information(self):
        """Test project information presentation"""
        print("\n📋 Testing Project Information")
        print("-" * 30)
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for project features
                features = [
                    "cost calculations",
                    "excel",
                    "csv import",
                    "rollups",
                    "project management",
                    "real-time",
                    "security",
                    "fastapi",
                    "next.js",
                    "oauth"
                ]
                
                print("   📊 Feature descriptions:")
                for feature in features:
                    present = feature in content
                    status = "✅" if present else "❌"
                    print(f"   {status} {feature.title()}")
                
                # Check for call-to-action elements
                cta_elements = [
                    ("sign in" in content, "Sign in call-to-action"),
                    ("login" in content, "Login references"),
                    ("google" in content, "Google authentication mention"),
                    ("secure" in content, "Security messaging")
                ]
                
                print("\n   🎯 Call-to-Action Elements:")
                for check, description in cta_elements:
                    status = "✅" if check else "❌"
                    print(f"   {status} {description}")
                    
            else:
                print(f"   ❌ Failed to load home page: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing project info: {e}")
    
    def test_responsive_design(self):
        """Test responsive design elements"""
        print("\n📱 Testing Responsive Design")
        print("-" * 25)
        
        try:
            # Test with mobile user agent
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            response = self.session.get(f"{self.base_url}/", headers=mobile_headers)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for responsive design elements
                responsive_checks = [
                    ("viewport" in content, "Viewport meta tag present"),
                    ("@media" in content, "Media queries present"),
                    ("grid" in content, "CSS Grid layout"),
                    ("flex" in content, "Flexbox layout"),
                    ("max-width" in content, "Responsive containers")
                ]
                
                for check, description in responsive_checks:
                    status = "✅" if check else "❌"
                    print(f"   {status} {description}")
                    
            else:
                print(f"   ❌ Mobile request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing responsive design: {e}")
    
    def test_security_features(self):
        """Test security-related features"""
        print("\n🔒 Testing Security Features")
        print("-" * 25)
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check security messaging
                security_checks = [
                    ("secure" in content, "Security messaging"),
                    ("oauth" in content, "OAuth mention"),
                    ("authorized users" in content, "Authorization info"),
                    ("google authentication" in content, "Google auth info"),
                    ("restricted" in content, "Access restriction info")
                ]
                
                for check, description in security_checks:
                    status = "✅" if check else "❌"
                    print(f"   {status} {description}")
                
                # Check for security headers (basic)
                headers = response.headers
                header_checks = [
                    ('Content-Type' in headers, "Content-Type header"),
                    ('X-Frame-Options' in headers, "X-Frame-Options header"),
                    ('X-Content-Type-Options' in headers, "X-Content-Type-Options header")
                ]
                
                print("\n   🛡️  Security Headers:")
                for check, description in header_checks:
                    status = "✅" if check else "⚠️"
                    print(f"   {status} {description}")
                    
            else:
                print(f"   ❌ Failed to check security features: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing security: {e}")
    
    def run_all_tests(self):
        """Run all home page tests"""
        print("🧪 Home Page & User Flow Tests")
        print("=" * 50)
        print("Testing the public home page and authentication flow")
        print(f"Base URL: {self.base_url}")
        
        self.test_home_page_unauthenticated()
        self.test_login_flow_initiation()
        self.test_post_login_behavior()
        self.test_project_information()
        self.test_responsive_design()
        self.test_security_features()
        
        print("\n" + "=" * 50)
        print("📋 Test Summary:")
        print("✅ Home page should load with project information")
        print("✅ Login button should initiate OAuth flow")
        print("✅ Project features should be clearly described")
        print("✅ Security messaging should be present")
        print("✅ Responsive design elements should be included")
        
        print("\n🔧 Next Steps:")
        print("1. Configure Google OAuth credentials")
        print("2. Set ALLOWED_USERS in .env file")
        print("3. Test complete OAuth flow via browser")
        print("4. Verify post-login dashboard functionality")

def simulate_user_journey():
    """Simulate a complete user journey"""
    print("\n🚶 Simulating Complete User Journey")
    print("-" * 35)
    
    steps = [
        "1. User visits home page (/) → sees project info + login button",
        "2. User clicks 'Sign in with Google' → redirected to Google OAuth",
        "3. User authenticates with Google → Google redirects to /auth/callback",
        "4. Backend verifies state, checks authorization, creates session",
        "5. User redirected to frontend dashboard with active session",
        "6. If user visits home page again → auto-redirected to dashboard",
        "7. User can logout → session cleared, redirected to home page"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n💡 Key Features:")
    print("   • Seamless OAuth integration")
    print("   • Automatic post-login redirects")
    print("   • Session-based authentication")
    print("   • Professional project presentation")
    print("   • Mobile-responsive design")

if __name__ == "__main__":
    print("Home Page & Authentication Flow Test Suite")
    print("This tests the public home page and OAuth integration")
    input("Press Enter to start tests...")
    
    tester = HomePageTester()
    tester.run_all_tests()
    
    simulate_user_journey()
    
    print("\n✨ Testing complete!")
    print("\nTo test the complete flow:")
    print("1. Start backend: python main.py")
    print("2. Visit: http://localhost:8000/")
    print("3. Click 'Sign in with Google'")
    print("4. Complete OAuth flow")
    print("5. Verify dashboard access")
