# Google OAuth 2.0 Setup Guide

This guide will help you set up Google OAuth 2.0 authentication for your GC Estimator backend.

## Prerequisites

1. **Google Cloud Console Account**: You need access to [Google Cloud Console](https://console.cloud.google.com/)
2. **Project Setup**: Create or select a project in Google Cloud Console

## Step 1: Configure Google Cloud Console

### 1.1 Enable Google+ API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Library**
3. Search for "Google+ API" and enable it
4. Also enable "Google OAuth2 API" if available

### 1.2 Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - Choose **External** user type
   - Fill in required fields (App name, User support email, Developer contact)
   - Add your domain to authorized domains if deploying to production
4. For Application type, choose **Web application**
5. Configure the OAuth client:
   - **Name**: `GC Estimator Backend`
   - **Authorized JavaScript origins**: 
     - `http://localhost:8000` (for development)
     - Add your production domain when deploying
   - **Authorized redirect URIs**:
     - `http://localhost:8000/auth/callback` (for development)
     - Add your production callback URL when deploying

### 1.3 Download Credentials
1. After creating, you'll get a **Client ID** and **Client Secret**
2. Copy these values - you'll need them for the environment configuration

## Step 2: Backend Configuration

### 2.1 Install Dependencies
The OAuth dependencies have been added to `requirements.txt`. Install them:

```bash
# If using virtual environment (recommended)
pip install -r requirements.txt

# If using Docker, rebuild the container
docker-compose build backend
```

### 2.2 Environment Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your Google OAuth credentials:
```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here

# JWT Secret Key - Generate a secure random key
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Application URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# User Authorization - Comma-separated list of allowed email addresses
ALLOWED_USERS=your_email@example.com,admin@company.com
```

**Important**: 
- Replace `your_actual_google_client_id_here` with your actual Google Client ID
- Replace `your_actual_google_client_secret_here` with your actual Google Client Secret  
- Replace `your_email@example.com` with your actual email address
- Generate a strong, random SECRET_KEY for JWT token signing
- Never commit the `.env` file to version control

### 2.3 Generate a Secure JWT Secret Key
You can generate a secure secret key using Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use this command:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: API Endpoints

The following OAuth endpoints are now available:

### Authentication Endpoints
- **`GET /auth/login`** - Initiate Google OAuth login with CSRF protection
- **`GET /auth/callback`** - OAuth callback handler with state verification and user authorization
- **`POST /auth/logout`** - Secure logout with complete session cleanup
- **`GET /auth/user`** - Get current user information (JWT-based)
- **`GET /auth/session`** - Get current session information (session-based)
- **`GET /auth/verify`** - Verify JWT token validity
- **`GET /auth/admin/allowed-users`** - Get list of allowed users (admin only)

### Public Endpoints (No Authentication Required)
- **`GET /`** - Public home page with project information and login
- **`GET /api`** - API root endpoint with JSON information
- **`GET /public/status`** - Public system status
- **`GET /health`** - Health check endpoint
- **`GET /docs`** - Interactive API documentation

### Authenticated User Endpoints
- **`GET /dashboard`** - User dashboard with API testing interface (requires session)

### Protected Endpoints
All estimate-related endpoints now require authentication:
- `GET /api/estimates` - List estimates
- `POST /api/estimates` - Create estimate
- `GET /api/estimates/{id}` - Get estimate
- `PUT /api/estimates/{id}` - Update estimate
- `DELETE /api/estimates/{id}` - Delete estimate
- `POST /api/estimates/import` - Import QTO file
- And all item-related endpoints...

## Step 4: Frontend Integration

### 4.1 Authentication Flow
1. **Login**: Direct users to `GET /auth/login`
2. **Callback**: Google redirects to `/auth/callback` with token
3. **Token Storage**: Frontend receives token and stores it (localStorage/sessionStorage)
4. **API Calls**: Include token in Authorization header: `Bearer <token>`

### 4.2 Frontend Implementation Example
```javascript
// Login
window.location.href = 'http://localhost:8000/auth/login';

// After callback, extract token from URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
if (token) {
    localStorage.setItem('authToken', token);
}

// API calls with authentication
const response = await fetch('http://localhost:8000/api/estimates', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'Content-Type': 'application/json'
    }
});
```

## Step 5: Testing

### 5.1 Start the Backend
```bash
# Using Docker
docker-compose up backend

# Or directly with Python
cd backend
python main.py
```

### 5.2 Test OAuth Flow
1. Visit `http://localhost:8000/auth/login` in your browser
2. You should be redirected to Google's login page
3. After successful login, you should be redirected back with a token
4. Test protected endpoints using the token

### 5.3 API Documentation
Visit `http://localhost:8000/docs` to see the interactive API documentation with all the new OAuth endpoints.

## Security Features

### CSRF Protection ✅
The implementation includes robust CSRF (Cross-Site Request Forgery) protection using OAuth state parameters:

1. **State Token Generation**: A cryptographically secure random state token is generated for each login attempt
2. **Session Storage**: The state token is stored in the server-side session with a timestamp
3. **State Verification**: The callback handler verifies that the returned state matches the stored state
4. **Single-Use Tokens**: State tokens are automatically cleared after use
5. **Expiration**: State tokens expire after 10 minutes for added security

### How CSRF Protection Works
1. **Login Request**: User visits `/auth/login`
   - Server generates random state token (32 bytes, URL-safe)
   - State token stored in session with timestamp
   - User redirected to Google with state parameter

2. **Google Callback**: Google redirects back with state parameter
   - Server extracts state from query parameters
   - Verifies state matches stored session value
   - Checks state hasn't expired (10 minute limit)
   - Clears state from session (single-use)
   - Proceeds with token exchange only if state is valid

3. **Attack Prevention**: 
   - Prevents malicious sites from initiating OAuth flows
   - Ensures callback responses are tied to legitimate requests
   - Protects against session fixation attacks

### User Authorization System ✅
The system includes robust user authorization to restrict access to only approved users:

1. **Allow-List Configuration**: Only users in the `ALLOWED_USERS` environment variable can access the application
2. **OAuth Callback Authorization**: Email addresses are checked immediately after Google authentication
3. **Runtime Authorization**: User authorization is verified on every API request (not just login)
4. **No Automatic Sign-ups**: Users are not automatically created - only pre-approved emails are allowed
5. **Case-Insensitive Matching**: Email comparison ignores case differences

### How User Authorization Works
1. **Configuration**: Set `ALLOWED_USERS=email1@domain.com,email2@domain.com` in `.env`
2. **OAuth Callback**: After Google authenticates the user:
   - Extract user's email from Google profile
   - Check if email exists in allowed users list
   - If authorized: Create JWT token and proceed
   - If unauthorized: Return 403 error with clear message
3. **API Requests**: Every protected endpoint call:
   - Verifies JWT token validity
   - Double-checks user email against current allowed users list
   - Allows request only if user is still authorized

### Authorization Levels
- **Single User Mode**: Set `ALLOWED_USERS=your_email@gmail.com` for personal use
- **Multi-User Mode**: Set `ALLOWED_USERS=user1@domain.com,user2@domain.com,user3@domain.com`
- **Admin Endpoint**: First user in the list has admin privileges (can view allowed users list)

### Session Management System ✅
The system provides comprehensive session management alongside JWT tokens:

1. **Dual Authentication**: Supports both session-based and JWT token authentication
2. **Secure Sessions**: 8-hour session lifetime with activity tracking
3. **Session Security**: SameSite cookies, secure session storage, automatic cleanup
4. **Activity Monitoring**: Last activity timestamps and login time tracking
5. **Complete Logout**: Full session clearing with security confirmation

### How Session Management Works
1. **Login**: After successful OAuth, both session and JWT token are created
2. **Session Storage**: User info stored securely in server-side session
3. **Request Authentication**: Endpoints accept either session or JWT authentication
4. **Activity Updates**: Session activity updated on each authenticated request
5. **Logout**: Complete session cleanup and token invalidation guidance
6. **Expiration**: Sessions automatically expire after 8 hours of inactivity

### Session vs JWT Authentication
- **Sessions**: Ideal for web applications, automatic cookie handling, server-side state
- **JWT Tokens**: Ideal for API clients, stateless, mobile app friendly
- **Flexible**: All endpoints support both authentication methods
- **Security**: Both methods include authorization checks and user validation

### Public Home Page System ✅
The application features a comprehensive public home page with professional presentation:

1. **Project Information**: Detailed description of GC Estimator features and capabilities
2. **Professional Design**: Modern, responsive UI with gradient backgrounds and animations
3. **Login Integration**: Prominent "Sign in with Google" button with OAuth flow initiation
4. **Post-Login Behavior**: Authenticated users automatically redirected to dashboard
5. **Security Messaging**: Clear information about authentication requirements and authorized access

### Home Page Features
- **Responsive Design**: Mobile-friendly layout with CSS Grid and Flexbox
- **Interactive Elements**: Hover effects, loading states, and smooth transitions
- **Feature Showcase**: Six key feature cards highlighting application capabilities
- **Technology Stack**: Display of modern technologies used in development
- **Security Indicators**: Clear messaging about OAuth 2.0 and user authorization
- **Professional Branding**: Consistent visual identity and professional presentation

### User Flow
1. **Unauthenticated**: Visit `/` → see home page with project info and login button
2. **Login Initiation**: Click "Sign in with Google" → redirect to OAuth flow
3. **Authentication**: Complete Google OAuth → callback creates session
4. **Post-Login**: Authenticated users visiting `/` → auto-redirect to `/dashboard`
5. **Dashboard**: Interactive dashboard with API testing and user information
6. **Logout**: Complete session cleanup and redirect to home page

## Security Notes

1. **HTTPS in Production**: Always use HTTPS in production
2. **Secure Secret Key**: Use a strong, randomly generated SECRET_KEY
3. **Environment Variables**: Never commit credentials to version control
4. **Token Expiration**: Tokens expire after 30 minutes by default
5. **CORS Configuration**: Update CORS_ORIGINS for your production domains
6. **CSRF Protection**: State parameters prevent cross-site request forgery
7. **Session Security**: Sessions use secure cookies with SameSite protection

## Troubleshooting

### Common Issues
1. **"Invalid client" error**: Check your Google Client ID and Secret
2. **Redirect URI mismatch**: Ensure callback URL matches Google Console settings
3. **CORS errors**: Verify CORS_ORIGINS includes your frontend URL
4. **Token validation failed**: Check SECRET_KEY consistency
5. **"Invalid or missing state parameter" error**: 
   - Ensure sessions are working (check SessionMiddleware setup)
   - Verify SECRET_KEY is consistent across requests
   - Check that cookies are enabled in browser
   - Ensure login and callback happen within 10 minutes
6. **Session not persisting**: 
   - Check cookie settings (SameSite, Secure flags)
   - Verify SECRET_KEY is set correctly
   - Ensure browser accepts cookies

### Debug Mode
Set environment variable for more detailed error messages:
```bash
export FASTAPI_DEBUG=true
```

## Next Steps

1. **Database Integration**: Replace in-memory storage with a proper database
2. **User Management**: Add user roles and permissions
3. **Session Management**: Implement refresh tokens
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Logging**: Add comprehensive logging for security monitoring
