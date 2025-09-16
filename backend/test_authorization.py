#!/usr/bin/env python3
"""
Test script to verify user authorization system
"""
import os
import sys
from auth import is_user_authorized, get_allowed_users_list

def test_authorization_logic():
    """Test the authorization logic with different scenarios"""
    print("🔐 Testing User Authorization System")
    print("=" * 50)
    
    # Test 1: Check current configuration
    print("\n📋 Current Configuration:")
    allowed_users = get_allowed_users_list()
    if allowed_users:
        print(f"✅ Allowed users configured: {len(allowed_users)}")
        for i, email in enumerate(allowed_users, 1):
            print(f"   {i}. {email}")
    else:
        print("⚠️  No allowed users configured (development mode)")
    
    # Test 2: Authorization checks
    print("\n🧪 Authorization Tests:")
    
    test_emails = [
        "admin@example.com",
        "user@gmail.com", 
        "unauthorized@domain.com",
        "ADMIN@EXAMPLE.COM",  # Test case sensitivity
        ""  # Empty email
    ]
    
    for email in test_emails:
        if email:
            is_authorized = is_user_authorized(email)
            status = "✅ AUTHORIZED" if is_authorized else "❌ DENIED"
            print(f"   {email:<25} → {status}")
        else:
            print(f"   {'(empty email)':<25} → ❌ DENIED")
    
    # Test 3: Environment variable check
    print("\n🔧 Environment Check:")
    allowed_users_env = os.getenv('ALLOWED_USERS', '')
    if allowed_users_env:
        print(f"✅ ALLOWED_USERS env var: {allowed_users_env}")
    else:
        print("⚠️  ALLOWED_USERS environment variable not set")
    
    # Test 4: Security recommendations
    print("\n🛡️  Security Recommendations:")
    if not allowed_users:
        print("   ⚠️  Set ALLOWED_USERS in your .env file")
        print("   ⚠️  Current setup allows any authenticated Google user")
    else:
        print("   ✅ User authorization is properly configured")
    
    if len(allowed_users) == 1:
        print("   ℹ️  Single user mode - only one user has access")
    elif len(allowed_users) > 1:
        print(f"   ℹ️  Multi-user mode - {len(allowed_users)} users have access")
    
    print("\n📝 How to configure:")
    print("   1. Create a .env file in the backend directory")
    print("   2. Add: ALLOWED_USERS=your_email@example.com,other@example.com")
    print("   3. Restart the server")
    
    return len(allowed_users) > 0

def simulate_oauth_callback(email: str):
    """Simulate what happens in OAuth callback"""
    print(f"\n🔄 Simulating OAuth callback for: {email}")
    
    if not email:
        print("   ❌ No email provided by Google")
        return False
    
    if is_user_authorized(email):
        print(f"   ✅ User {email} authorized - would create JWT token")
        return True
    else:
        print(f"   ❌ User {email} denied access - would return 403 error")
        return False

if __name__ == "__main__":
    print("Testing Authorization System")
    print("Make sure you have configured ALLOWED_USERS in your .env file")
    print("Example: ALLOWED_USERS=your_email@gmail.com,admin@company.com")
    print()
    
    # Run tests
    has_config = test_authorization_logic()
    
    # Interactive test
    print("\n" + "="*50)
    print("🎯 Interactive Test")
    
    if has_config:
        while True:
            email = input("\nEnter an email to test (or 'quit' to exit): ").strip()
            if email.lower() == 'quit':
                break
            simulate_oauth_callback(email)
    else:
        print("Configure ALLOWED_USERS first, then run this test again.")
    
    print("\n✨ Test complete!")
