# =============================================================================
# AUTHENTICATION ROUTES MODULE  
# =============================================================================
"""
Authentication Routes for Ask My PDF Chatbot

This module defines the URL routes for authentication endpoints using Flask Blueprint.
It connects HTTP endpoints to their corresponding controller functions.

Endpoints Provided:
- POST /auth/signup        - User registration
- POST /auth/login         - User authentication  
- DELETE /auth/delete-account - Account deletion

URL Structure:
All auth routes are prefixed with '/auth' for API organization:
- Base URL: http://localhost:5000/auth/
- Full endpoints: 
  * http://localhost:5000/auth/signup
  * http://localhost:5000/auth/login
  * http://localhost:5000/auth/delete-account

Architecture:
- Uses Flask Blueprint for modular route organization
- Separates routing logic from business logic (controllers)
- Enables easy integration with main Flask app
- Allows for future auth route extensions

Author: [Your Team]
Created for: CDAC Project - Ask My PDF Chatbot
"""

from flask import Blueprint
from controllers.auth_controller import signup, login, delete_account

# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

# Create authentication blueprint with URL prefix
# This groups all auth routes under '/auth' for better API organization
auth_bp = Blueprint(
    "auth_bp",                    # Blueprint name (internal identifier)
    __name__,                     # Blueprint import name
    url_prefix="/auth"            # URL prefix for all routes in this blueprint
)

# =============================================================================
# ROUTE DEFINITIONS
# =============================================================================

# User Registration Endpoint
# POST /auth/signup
# Purpose: Create new user account with email, name, and password
auth_bp.route("/signup", methods=["POST"])(signup)

# User Login Endpoint  
# POST /auth/login
# Purpose: Authenticate user and return JWT token
auth_bp.route("/login", methods=["POST"])(login)

# Account Deletion Endpoint
# DELETE /auth/delete-account  
# Purpose: Delete user account (requires authentication)
auth_bp.route("/delete-account", methods=["DELETE"])(delete_account)

# =============================================================================
# INTEGRATION NOTES FOR DEVELOPERS
# =============================================================================
"""
How to Use This Blueprint:

1. REGISTER WITH MAIN APP:
   In your main app.py file:
   
   from routes.auth_routes import auth_bp
   app.register_blueprint(auth_bp)

2. URL PATTERNS:
   With app running on localhost:5000, endpoints become:
   - POST http://localhost:5000/auth/signup
   - POST http://localhost:5000/auth/login  
   - DELETE http://localhost:5000/auth/delete-account

3. FRONTEND INTEGRATION:
   Use these endpoints in your frontend API calls:
   
   // Signup
   fetch('/auth/signup', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({email, name, password})
   })
   
   // Login
   fetch('/auth/login', {
       method: 'POST', 
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({email, password})
   })
   
   // Delete Account
   fetch('/auth/delete-account', {
       method: 'DELETE',
       headers: {'Authorization': 'Bearer ' + token}
   })

4. ADDING NEW AUTH ROUTES:
   To add new authentication endpoints:
   
   # 1. Create controller function in auth_controller.py
   def reset_password():
       # Implementation here
       pass
   
   # 2. Import and add route here
   from controllers.auth_controller import reset_password
   auth_bp.route("/reset-password", methods=["POST"])(reset_password)

5. ERROR HANDLING:
   All routes return JSON responses with appropriate HTTP status codes.
   Check controller implementations for detailed response formats.

6. TESTING ROUTES:
   Use curl, Postman, or similar tools:
   
   # Test signup
   curl -X POST http://localhost:5000/auth/signup \
        -H "Content-Type: application/json" \
        -d '{"email":"test@test.com","name":"Test","password":"pass123"}'

Future Route Extensions:
- /auth/refresh-token (refresh JWT token)
- /auth/reset-password (password reset via email)
- /auth/verify-email (email verification)
- /auth/change-password (change password when logged in)
- /auth/profile (get/update user profile)
"""
