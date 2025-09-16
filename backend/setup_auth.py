#!/usr/bin/env python3
"""
Interactive setup script for OAuth and user authorization
"""
import os
import secrets
import re

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def setup_environment():
    """Interactive setup for .env file"""
    print("🔧 GC Estimator OAuth Setup")
    print("=" * 40)
    
    env_file = ".env"
    env_exists = os.path.exists(env_file)
    
    if env_exists:
        print(f"⚠️  {env_file} already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 Please provide the following information:")
    print("(You can get OAuth credentials from Google Cloud Console)")
    
    # Google OAuth Configuration
    print("\n1. Google OAuth Credentials:")
    google_client_id = input("   Google Client ID: ").strip()
    google_client_secret = input("   Google Client Secret: ").strip()
    
    if not google_client_id or not google_client_secret:
        print("❌ Google OAuth credentials are required!")
        return
    
    # User Authorization
    print("\n2. Authorized Users:")
    print("   Enter email addresses that should have access to the application.")
    print("   You can add multiple emails separated by commas.")
    
    allowed_users = []
    while True:
        email = input(f"   Email {len(allowed_users) + 1} (or press Enter to finish): ").strip()
        if not email:
            break
        
        if validate_email(email):
            allowed_users.append(email)
            print(f"   ✅ Added: {email}")
        else:
            print(f"   ❌ Invalid email format: {email}")
    
    if not allowed_users:
        print("❌ At least one authorized user is required!")
        return
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Application URLs
    print("\n3. Application URLs:")
    frontend_url = input("   Frontend URL (default: http://localhost:3000): ").strip()
    if not frontend_url:
        frontend_url = "http://localhost:3000"
    
    backend_url = input("   Backend URL (default: http://localhost:8000): ").strip()
    if not backend_url:
        backend_url = "http://localhost:8000"
    
    # CORS Origins
    cors_origins = f"{frontend_url},http://127.0.0.1:3000"
    
    # Create .env file content
    env_content = f"""# Google OAuth Configuration
# Get these from Google Cloud Console: https://console.cloud.google.com/
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}

# JWT Secret Key - Generated automatically
SECRET_KEY={secret_key}

# Application URLs
FRONTEND_URL={frontend_url}
BACKEND_URL={backend_url}

# CORS Origins (comma-separated)
CORS_ORIGINS={cors_origins}

# User Authorization - Comma-separated list of allowed email addresses
ALLOWED_USERS={','.join(allowed_users)}
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Configuration saved to {env_file}")
        print("\n📋 Summary:")
        print(f"   • Google Client ID: {google_client_id[:10]}...")
        print(f"   • Authorized users: {len(allowed_users)}")
        for i, email in enumerate(allowed_users, 1):
            print(f"     {i}. {email}")
        print(f"   • Frontend URL: {frontend_url}")
        print(f"   • Backend URL: {backend_url}")
        print(f"   • Secret key: Generated (32 bytes)")
        
        print("\n🚀 Next Steps:")
        print("   1. Make sure your Google OAuth redirect URI is set to:")
        print(f"      {backend_url}/auth/callback")
        print("   2. Start the backend server: python main.py")
        print("   3. Test authentication: visit /auth/login")
        
        print("\n⚠️  Security Notes:")
        print("   • Never commit the .env file to version control")
        print("   • Use HTTPS in production")
        print("   • Keep your Google Client Secret secure")
        
    except Exception as e:
        print(f"❌ Error writing {env_file}: {e}")

def test_configuration():
    """Test the current configuration"""
    print("\n🧪 Testing Configuration:")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run setup first.")
        return
    
    # Test imports
    try:
        from auth import get_allowed_users_list, is_user_authorized
        print("✅ Auth module imports successfully")
        
        allowed_users = get_allowed_users_list()
        if allowed_users:
            print(f"✅ {len(allowed_users)} authorized users configured")
            
            # Test authorization
            test_email = allowed_users[0]
            if is_user_authorized(test_email):
                print(f"✅ Authorization test passed for {test_email}")
            else:
                print(f"❌ Authorization test failed for {test_email}")
        else:
            print("⚠️  No authorized users configured")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

if __name__ == "__main__":
    print("Welcome to GC Estimator OAuth Setup!")
    print("\nThis script will help you configure:")
    print("• Google OAuth credentials")
    print("• User authorization (who can access the app)")
    print("• Application URLs and security settings")
    
    while True:
        print("\nOptions:")
        print("1. Setup new configuration")
        print("2. Test current configuration")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            setup_environment()
        elif choice == '2':
            test_configuration()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1, 2, or 3.")
