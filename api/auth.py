"""
OAuth 2.0 Authentication module for Google OAuth integration with CSRF protection
"""
import os
import secrets
from typing import Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import httpx
from jose import JWTError, jwt
from datetime import datetime, timedelta

# OAuth configuration
config = Config('.env')  # You'll need to create a .env file with your credentials

# OAuth settings - these should be set in your .env file
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-change-this-in-production')

# User Authorization - Comma-separated list of allowed email addresses
ALLOWED_USERS = config('ALLOWED_USERS', default='').split(',')
ALLOWED_USERS = [email.strip() for email in ALLOWED_USERS if email.strip()]  # Clean up whitespace

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Security scheme for JWT tokens
security = HTTPBearer()

class User:
    """User model for authenticated users"""
    def __init__(self, email: str, name: str, picture: str, sub: str):
        self.email = email
        self.name = name
        self.picture = picture
        self.sub = sub  # Google's unique user ID
        self.id = sub  # Use Google's sub as our user ID

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token with authorization check"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info from token payload
    email = payload.get("email")
    name = payload.get("name")
    picture = payload.get("picture")
    sub = payload.get("sub")
    
    if not all([email, name, sub]):
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Double-check authorization on every request (in case ALLOWED_USERS changed)
    if not is_user_authorized(email):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. User {email} is no longer authorized to access this application.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(email=email, name=name, picture=picture, sub=sub)

async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for optional auth)"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if payload is None:
            return None
            
        email = payload.get("email")
        name = payload.get("name")
        picture = payload.get("picture")
        sub = payload.get("sub")
        
        if not all([email, name, sub]):
            return None
            
        return User(email=email, name=name, picture=picture, sub=sub)
    except:
        return None

async def get_current_user_from_session(request: Request) -> Optional[User]:
    """Get current user from session (alternative to JWT)"""
    if not SessionManager.is_session_valid(request):
        return None
    
    user_info = SessionManager.get_session_user(request)
    if not user_info:
        return None
    
    # Update session activity
    SessionManager.update_session_activity(request)
    
    return User(
        email=user_info['email'],
        name=user_info['name'],
        picture=user_info['picture'],
        sub=user_info['sub']
    )

async def require_authentication(request: Request) -> User:
    """Require authentication via session or JWT token"""
    # First try session-based authentication
    session_user = await get_current_user_from_session(request)
    if session_user:
        return session_user
    
    # Fall back to JWT token authentication
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from fastapi.security import HTTPAuthorizationCredentials
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=auth_header.split(" ")[1]
            )
            return await get_current_user(credentials)
        except:
            pass
    
    # No valid authentication found
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Please log in to access this resource.",
        headers={"WWW-Authenticate": "Bearer"}
    )

def require_session_auth(request: Request) -> User:
    """Dependency for routes that require session-based authentication"""
    if not SessionManager.is_session_valid(request):
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid. Please log in again."
        )
    
    user_info = SessionManager.get_session_user(request)
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="No valid session found. Please log in."
        )
    
    # Update session activity
    SessionManager.update_session_activity(request)
    
    return User(
        email=user_info['email'],
        name=user_info['name'],
        picture=user_info['picture'],
        sub=user_info['sub']
    )

def generate_state_token() -> str:
    """Generate a cryptographically secure random state token for CSRF protection"""
    return secrets.token_urlsafe(32)

def store_oauth_state(request: Request, state: str) -> None:
    """Store OAuth state in session for CSRF verification"""
    request.session['oauth_state'] = state
    request.session['oauth_state_timestamp'] = datetime.utcnow().timestamp()

def verify_oauth_state(request: Request, received_state: str) -> bool:
    """Verify OAuth state parameter against stored session state"""
    stored_state = request.session.get('oauth_state')
    stored_timestamp = request.session.get('oauth_state_timestamp')
    
    # Clear the state from session after use (single-use)
    request.session.pop('oauth_state', None)
    request.session.pop('oauth_state_timestamp', None)
    
    if not stored_state or not stored_timestamp:
        return False
    
    # Check if state matches
    if stored_state != received_state:
        return False
    
    # Check if state hasn't expired (10 minutes max)
    current_time = datetime.utcnow().timestamp()
    if current_time - stored_timestamp > 600:  # 10 minutes
        return False
    
    return True

def is_user_authorized(email: str) -> bool:
    """Check if user email is in the allowed users list"""
    if not ALLOWED_USERS:
        # If no allowed users are configured, log a warning but allow access for development
        print(f"⚠️  WARNING: No ALLOWED_USERS configured. User {email} granted access.")
        return True
    
    return email.lower() in [allowed_email.lower() for allowed_email in ALLOWED_USERS]

def get_allowed_users_list() -> list:
    """Get the list of allowed users for debugging/admin purposes"""
    return ALLOWED_USERS.copy()

class UnauthorizedUserError(Exception):
    """Exception raised when user is not in the allowed users list"""
    pass

class SessionExpiredError(Exception):
    """Exception raised when user session has expired"""
    pass

class RouteProtectionError(Exception):
    """Exception raised when accessing protected route without authentication"""
    pass

class SessionManager:
    """Enhanced session management for user authentication"""
    
    @staticmethod
    def create_user_session(request: Request, user_info: dict) -> None:
        """Create a secure user session"""
        request.session['user'] = {
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info['picture'],
            'sub': user_info['sub'],
            'login_time': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        }
        request.session['authenticated'] = True
        
    @staticmethod
    def get_session_user(request: Request) -> Optional[dict]:
        """Get user info from session"""
        if not request.session.get('authenticated', False):
            return None
        return request.session.get('user')
    
    @staticmethod
    def update_session_activity(request: Request) -> None:
        """Update last activity timestamp"""
        if request.session.get('authenticated', False):
            if 'user' in request.session:
                request.session['user']['last_activity'] = datetime.utcnow().isoformat()
    
    @staticmethod
    def clear_user_session(request: Request) -> None:
        """Clear user session completely"""
        # Clear all session data
        request.session.clear()
    
    @staticmethod
    def is_session_valid(request: Request) -> bool:
        """Check if session is valid and not expired"""
        if not request.session.get('authenticated', False):
            return False
            
        user_info = request.session.get('user')
        if not user_info:
            return False
            
        # Check session age (max 8 hours)
        try:
            login_time = datetime.fromisoformat(user_info['login_time'])
            if datetime.utcnow() - login_time > timedelta(hours=8):
                return False
        except (KeyError, ValueError):
            return False
            
        # Check if user is still authorized
        return is_user_authorized(user_info['email'])

def init_oauth_middleware(app):
    """Initialize OAuth middleware with enhanced session management"""
    # Add session middleware with enhanced security
    app.add_middleware(
        SessionMiddleware, 
        secret_key=SECRET_KEY,
        max_age=28800,  # 8 hours (28800 seconds)
        same_site='lax',  # CSRF protection
        https_only=False,  # Set to True in production with HTTPS
        domain=None,  # Set to your domain in production
        path='/'  # Session available for all paths
    )
    return oauth
