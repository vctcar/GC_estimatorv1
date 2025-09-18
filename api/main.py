from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from typing import List, Optional
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import uuid

# Import OAuth authentication
from auth import (
    oauth, init_oauth_middleware, get_current_user, get_current_user_optional,
    create_access_token, User, ACCESS_TOKEN_EXPIRE_MINUTES,
    generate_state_token, store_oauth_state, verify_oauth_state,
    is_user_authorized, get_allowed_users_list, UnauthorizedUserError,
    SessionManager, require_authentication, require_session_auth,
    get_current_user_from_session
)

# Import your existing estimator modules
from schemas import Project, LineItem, Item, CostBreakdown
from qto import QTOLoader
from rollups import CostRollup

app = FastAPI(
    title="GC Estimator API",
    description="REST API for General Contractor Estimation Tool with OAuth 2.0",
    version="1.0.0"
)

# Initialize OAuth middleware
oauth_client = init_oauth_middleware(app)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for estimates (replace with database in production)
estimates_db = {}

# OAuth and Authentication Endpoints
@app.get("/auth/login")
async def login(request: Request):
    """Initiate Google OAuth login with CSRF protection"""
    # Generate and store CSRF state token
    state = generate_state_token()
    store_oauth_state(request, state)
    
    # Build redirect URI
    redirect_uri = request.url_for('auth_callback')
    
    # Initiate OAuth flow with state parameter
    return await oauth_client.google.authorize_redirect(
        request, 
        redirect_uri, 
        state=state
    )

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback from Google with CSRF protection"""
    try:
        # Extract state parameter from query string
        received_state = request.query_params.get('state')
        
        # Verify CSRF state parameter
        if not received_state or not verify_oauth_state(request, received_state):
            raise HTTPException(
                status_code=400, 
                detail="Invalid or missing state parameter - possible CSRF attack"
            )
        
        # Proceed with OAuth token exchange
        token = await oauth_client.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            user_email = user_info.get("email")
            user_name = user_info.get("name")
            
            # Check if user is authorized
            if not is_user_authorized(user_email):
                print(f"🚫 Unauthorized access attempt by: {user_email}")
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied. User {user_email} is not authorized to access this application."
                )
            
            print(f"✅ Authorized user logged in: {user_name} ({user_email})")
            
            # Create secure session for the user
            SessionManager.create_user_session(request, user_info)
            
            # Also create JWT token for API access (optional - session is primary)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user_info.get("sub"),
                    "email": user_email,
                    "name": user_name,
                    "picture": user_info.get("picture")
                },
                expires_delta=access_token_expires
            )
            
            # Redirect to frontend with token (session will be maintained via cookies)
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?token={access_token}&session=true"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to get user info")
            
    except HTTPException:
        # Re-raise HTTP exceptions (like CSRF errors)
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/auth/logout")
async def logout(request: Request):
    """Secure logout endpoint - clears session and invalidates authentication"""
    user_info = SessionManager.get_session_user(request)
    user_email = user_info.get('email', 'Unknown') if user_info else 'Unknown'
    
    # Clear the user session completely
    SessionManager.clear_user_session(request)
    
    print(f"🔓 User logged out: {user_email}")
    
    return {
        "message": "Logged out successfully",
        "session_cleared": True,
        "instructions": "Please also clear any stored JWT tokens on the client side"
    }

@app.get("/auth/session")
async def get_session_info(request: Request):
    """Get current session information"""
    if not SessionManager.is_session_valid(request):
        raise HTTPException(status_code=401, detail="No valid session")
    
    user_info = SessionManager.get_session_user(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Session data not found")
    
    # Update activity timestamp
    SessionManager.update_session_activity(request)
    
    return {
        "authenticated": True,
        "user": {
            "email": user_info['email'],
            "name": user_info['name'],
            "picture": user_info['picture']
        },
        "session_info": {
            "login_time": user_info['login_time'],
            "last_activity": user_info['last_activity']
        }
    }

@app.get("/auth/user")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture
    }

@app.get("/auth/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if the current token is valid"""
    return {"valid": True, "user": current_user.email}

@app.get("/auth/admin/allowed-users")
async def get_allowed_users(current_user: User = Depends(get_current_user)):
    """Get list of allowed users (admin endpoint)"""
    # Only allow the first authorized user to see this (basic admin check)
    allowed_users = get_allowed_users_list()
    if not allowed_users or current_user.email.lower() != allowed_users[0].lower():
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "allowed_users": allowed_users,
        "total_count": len(allowed_users),
        "current_user": current_user.email
    }

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Public home page with project information and authentication"""
    # Check if user is already authenticated
    current_user = await get_current_user_from_session(request)
    
    # Get frontend URL for redirects
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # If user is authenticated, redirect to application
    if current_user:
        return RedirectResponse(url=f"{frontend_url}/dashboard")
    
    # Serve home page for unauthenticated users
    try:
        with open("templates/home.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to simple HTML if template file not found
        simple_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GC Estimator v1</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                .container { max-width: 800px; margin: 0 auto; }
                .login-btn { background: #4285f4; color: white; padding: 10px 20px; 
                           text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏗️ GC Estimator v1</h1>
                <p>Professional Construction Cost Estimation Tool</p>
                <p>Please sign in to access the application.</p>
                <a href="/auth/login" class="login-btn">Sign in with Google</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=simple_html)

@app.get("/api")
async def api_root():
    """API root endpoint - returns JSON information"""
    return {
        "message": "GC Estimator API is running", 
        "version": "1.0.0",
        "authentication": "OAuth 2.0 with Google",
        "documentation": "/docs",
        "login": "/auth/login",
        "home": "/"
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page for authenticated users"""
    # Require authentication
    current_user = await get_current_user_from_session(request)
    if not current_user:
        # Redirect to home page if not authenticated
        return RedirectResponse(url="/")
    
    # Create a simple dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - GC Estimator v1</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f8f9fa;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 1.8rem;
            }}
            
            .user-info {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 0.5rem;
            }}
            
            .user-details {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .user-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(255,255,255,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }}
            
            .logout-btn {{
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                text-decoration: none;
                transition: all 0.3s ease;
            }}
            
            .logout-btn:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 2rem auto;
                padding: 0 2rem;
            }}
            
            .welcome-card {{
                background: white;
                border-radius: 10px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .quick-actions {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .action-card {{
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                cursor: pointer;
                border: 1px solid #e9ecef;
            }}
            
            .action-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            }}
            
            .action-icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }}
            
            .action-title {{
                font-size: 1.2rem;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 0.5rem;
            }}
            
            .action-description {{
                color: #6c757d;
                font-size: 0.9rem;
            }}
            
            .api-info {{
                background: #e8f5e8;
                border: 1px solid #c3e6c3;
                border-radius: 10px;
                padding: 1.5rem;
                margin-top: 2rem;
            }}
            
            .api-info h3 {{
                color: #155724;
                margin-bottom: 1rem;
            }}
            
            .api-endpoints {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }}
            
            .endpoint {{
                background: white;
                padding: 0.8rem;
                border-radius: 5px;
                border: 1px solid #c3e6c3;
                font-family: monospace;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <header class="header">
            <h1>🏗️ GC Estimator v1 - Dashboard</h1>
            <div class="user-info">
                <div class="user-details">
                    <div class="user-avatar">👤</div>
                    <div>
                        <div><strong>{current_user.name}</strong></div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">{current_user.email}</div>
                    </div>
                </div>
                <button onclick="logout()" class="logout-btn">Logout</button>
            </div>
        </header>
        
        <div class="container">
            <div class="welcome-card">
                <h2>Welcome to GC Estimator, {current_user.name.split()[0]}! 👋</h2>
                <p>You're successfully authenticated and ready to start creating construction estimates. 
                   This is your dashboard where you can manage projects, create estimates, and access all features.</p>
            </div>
            
            <div class="quick-actions">
                <div class="action-card" onclick="window.open('/docs', '_blank')">
                    <div class="action-icon">📖</div>
                    <div class="action-title">API Documentation</div>
                    <div class="action-description">Explore interactive API documentation</div>
                </div>
                
                <div class="action-card" onclick="testAPI('/api/estimates')">
                    <div class="action-icon">📊</div>
                    <div class="action-title">View Estimates</div>
                    <div class="action-description">Access your construction estimates</div>
                </div>
                
                <div class="action-card" onclick="testAPI('/auth/session')">
                    <div class="action-icon">🔐</div>
                    <div class="action-title">Session Info</div>
                    <div class="action-description">View your current session details</div>
                </div>
                
                <div class="action-card" onclick="testAPI('/auth/admin/allowed-users')">
                    <div class="action-icon">👥</div>
                    <div class="action-title">User Management</div>
                    <div class="action-description">Manage authorized users (admin only)</div>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🚀 Available API Endpoints</h3>
                <p>Your session is active and you can now access all protected endpoints:</p>
                <div class="api-endpoints">
                    <div class="endpoint">GET /api/estimates</div>
                    <div class="endpoint">POST /api/estimates</div>
                    <div class="endpoint">GET /auth/session</div>
                    <div class="endpoint">GET /auth/user</div>
                    <div class="endpoint">POST /api/estimates/import</div>
                    <div class="endpoint">GET /api/estimates/{{id}}/rollup</div>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem;">
                    💡 <strong>Next Steps:</strong> Your frontend application should integrate with these endpoints 
                    to provide the full GC Estimator experience.
                </p>
            </div>
        </div>
        
        <script>
            async function logout() {{
                try {{
                    const response = await fetch('/auth/logout', {{ method: 'POST' }});
                    const result = await response.json();
                    alert(result.message);
                    window.location.href = '/';
                }} catch (error) {{
                    console.error('Logout error:', error);
                    alert('Logout failed. Please try again.');
                }}
            }}
            
            async function testAPI(endpoint) {{
                try {{
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    // Create a modal to show the response
                    const modal = document.createElement('div');
                    modal.style.cssText = `
                        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                        background: rgba(0,0,0,0.7); display: flex; align-items: center;
                        justify-content: center; z-index: 1000;
                    `;
                    
                    const content = document.createElement('div');
                    content.style.cssText = `
                        background: white; padding: 2rem; border-radius: 10px;
                        max-width: 600px; max-height: 80vh; overflow: auto;
                        position: relative;
                    `;
                    
                    content.innerHTML = `
                        <h3>API Response: ${{endpoint}}</h3>
                        <button onclick="this.closest('div[style*=fixed]').remove()" 
                                style="position: absolute; top: 10px; right: 15px; border: none; 
                                       background: none; font-size: 1.5rem; cursor: pointer;">×</button>
                        <pre style="background: #f8f9fa; padding: 1rem; border-radius: 5px; 
                                   overflow-x: auto; font-size: 0.9rem;">${{JSON.stringify(data, null, 2)}}</pre>
                    `;
                    
                    modal.appendChild(content);
                    document.body.appendChild(modal);
                    
                    modal.addEventListener('click', (e) => {{
                        if (e.target === modal) modal.remove();
                    }});
                    
                }} catch (error) {{
                    alert(`Error testing ${{endpoint}}: ${{error.message}}`);
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)

@app.get("/public/status")
async def public_status():
    """Public status endpoint - shows system status without authentication"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "authentication_required": True,
        "login_url": "/auth/login"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/estimates")
async def list_estimates(request: Request, current_user: User = Depends(require_authentication)):
    """List all estimates for dashboard (requires authentication)"""
    estimates = []
    for estimate_id, estimate in estimates_db.items():
        estimates.append({
            "id": estimate_id,
            "name": estimate.get("name", "Unnamed Estimate"),
            "client": estimate.get("client", ""),
            "total": estimate.get("total", 0),
            "status": estimate.get("status", "Draft"),
            "created": estimate.get("created", ""),
            "lastModified": estimate.get("lastModified", "")
        })
    return {"estimates": estimates}

@app.post("/api/estimates")
async def create_estimate(request: Request, project_data: dict, current_user: User = Depends(require_authentication)):
    """Create a new empty estimate or from template (requires authentication)"""
    estimate_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_estimate = {
        "id": estimate_id,
        "name": project_data.get("name", "New Estimate"),
        "client": project_data.get("client", ""),
        "description": project_data.get("description", ""),
        "overhead_percent": project_data.get("overhead_percent", 15.0),
        "profit_percent": project_data.get("profit_percent", 10.0),
        "aace_class": project_data.get("aace_class", "Class 3"),
        "status": "Draft",
        "created": now,
        "lastModified": now,
        "items": [],
        "metadata": project_data.get("metadata", {})
    }
    
    estimates_db[estimate_id] = new_estimate
    return {"estimate": new_estimate, "message": "Estimate created successfully"}

@app.post("/api/estimates/import")
async def import_qto(request: Request, file: UploadFile = File(...), current_user: User = Depends(require_authentication)):
    """Upload and parse a QTO Excel/CSV file (requires authentication)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV (.csv)")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Parse the file using your existing QTOLoader
        loader = QTOLoader()
        df = loader.load_excel(temp_file_path)
        items = loader.parse_line_items(df)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Convert items to dictionaries for JSON response
        line_items = []
        for item in items:
            line_items.append({
                "id": str(uuid.uuid4()),
                "phase": item.phase,
                "item": item.item,
                "unit": item.unit,
                "quantity": item.quantity,
                "waste": item.waste,
                "unit_cost": item.unit_cost,
                "lump_sum": item.lump_sum,
                "subtotal": item.subtotal
            })
        
        return {
            "message": f"Successfully imported {len(line_items)} items",
            "line_items": line_items,
            "total_items": len(line_items)
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/estimates/{estimate_id}")
async def get_estimate(request: Request, estimate_id: str, current_user: User = Depends(require_authentication)):
    """Fetch an estimate's data (meta, line items) (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    return {"estimate": estimate}

@app.put("/api/estimates/{estimate_id}")
async def update_estimate(request: Request, estimate_id: str, update_data: dict, current_user: User = Depends(require_authentication)):
    """Update project metadata (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Update allowed fields
    allowed_fields = ["name", "client", "description", "overhead_percent", "profit_percent", "aace_class", "status", "metadata"]
    for field in allowed_fields:
        if field in update_data:
            estimate[field] = update_data[field]
    
    estimate["lastModified"] = datetime.now().isoformat()
    estimates_db[estimate_id] = estimate
    
    return {"estimate": estimate, "message": "Estimate updated successfully"}

@app.post("/api/estimates/{estimate_id}/items")
async def add_item(request: Request, estimate_id: str, item_data: dict, current_user: User = Depends(require_authentication)):
    """Add a new line item to estimate (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Create new item with ID
    new_item = {
        "id": str(uuid.uuid4()),
        "phase": item_data.get("phase", ""),
        "item": item_data.get("item", ""),
        "unit": item_data.get("unit", ""),
        "quantity": item_data.get("quantity", 0),
        "waste": item_data.get("waste", 0),
        "unit_cost": item_data.get("unit_cost", 0),
        "lump_sum": item_data.get("lump_sum", 0),
        "subtotal": item_data.get("subtotal", 0)
    }
    
    # Add to estimate items
    if "items" not in estimate:
        estimate["items"] = []
    estimate["items"].append(new_item)
    
    # Update last modified
    estimate["lastModified"] = datetime.now().isoformat()
    estimates_db[estimate_id] = estimate
    
    return {"item": new_item, "message": "Item added successfully"}

@app.put("/api/estimates/{estimate_id}/items/{item_id}")
async def update_item(request: Request, estimate_id: str, item_id: str, item_data: dict, current_user: User = Depends(require_authentication)):
    """Update an existing line item (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Find and update the item
    for item in estimate.get("items", []):
        if item["id"] == item_id:
            # Update item fields
            allowed_fields = ["phase", "item", "unit", "quantity", "waste", "unit_cost", "lump_sum", "subtotal"]
            for field in allowed_fields:
                if field in item_data:
                    item[field] = item_data[field]
            
            # Update estimate last modified
            estimate["lastModified"] = datetime.now().isoformat()
            estimates_db[estimate_id] = estimate
            
            return {"item": item, "message": "Item updated successfully"}
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/api/estimates/{estimate_id}/items/{item_id}")
async def delete_item(request: Request, estimate_id: str, item_id: str, current_user: User = Depends(require_authentication)):
    """Delete a line item from estimate (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Find and remove the item
    for i, item in enumerate(estimate.get("items", [])):
        if item["id"] == item_id:
            estimate["items"].pop(i)
            estimate["lastModified"] = datetime.now().isoformat()
            estimates_db[estimate_id] = estimate
            return {"message": "Item deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/api/estimates/{estimate_id}/rollup")
async def get_rollup(request: Request, estimate_id: str, current_user: User = Depends(require_authentication)):
    """Run cost calculations and return rollup summary (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    try:
        # Create CostRollup instance with estimate data
        items = estimate.get("items", [])
        
        # Convert items to Item objects for rollup calculation
        items_list = []
        for item in items:
            # Create Item object based on the actual schema
            item_obj = Item(
                phase_code=item["phase"],
                code=item.get("item", ""),
                description=item.get("item", ""),
                uom=item["unit"],
                quantity=item["quantity"],
                waste_pct=item["waste"],
                material_unit_cost=item["unit_cost"],
                subcontract_lump_sum=item["lump_sum"]
            )
            items_list.append(item_obj)
        
        # Create project for rollup
        project = Project(
            name=estimate["name"],
            estimate_class=estimate.get("aace_class", "Class 3"),
            overhead_pct=estimate.get("overhead_percent", 15.0) / 100.0,
            profit_pct=estimate.get("profit_percent", 10.0) / 100.0
        )
        
        # Calculate rollup
        rollup = CostRollup(project, items_list)
        summary = rollup.create_summary_report()
        
        return {
            "estimate_id": estimate_id,
            "rollup": summary,
            "project_info": {
                "name": project.name,
                "client": project.client,
                "overhead_percent": project.overhead_percent,
                "profit_percent": project.profit_percent,
                "aace_class": project.aace_class
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating rollup: {str(e)}")

@app.delete("/api/estimates/{estimate_id}")
async def delete_estimate(request: Request, estimate_id: str, current_user: User = Depends(require_authentication)):
    """Delete an estimate (requires authentication)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    del estimates_db[estimate_id]
    return {"message": "Estimate deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
