"""
AUTH UTILS - JWT Authentication Utilities
=========================================

This module provides JWT token handling and route protection for the application.
It includes decorators and utilities for securing API endpoints.

Features Implemented:
- ✅ JWT token decoding and validation
- ✅ @require_auth decorator for protecting routes
- ✅ Automatic token extraction from Authorization headers
- ✅ User context injection (g.user_id, g.user_email, etc.)
- ✅ Comprehensive error handling for expired/invalid tokens

Usage Example:
    @app.route('/protected-endpoint')
    @require_auth
    def protected_function():
        user_id = g.user_id  # Available after @require_auth
        return f"Hello user {user_id}"

Author: Your Name
Date: August 2025
Purpose: JWT authentication middleware for Ask My PDF Chatbot
"""

from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# JWT configuration - must match the settings in auth_service.py
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
JWT_ALGORITHM = "HS256"

# =============================================================================
# JWT TOKEN UTILITIES
# =============================================================================

def decode_jwt(token: str):
    """
    Decode and validate JWT token
    
    This function verifies the JWT token signature and expiration.
    
    Args:
        token (str): JWT token string
    
    Returns:
        dict: Decoded token payload containing user information
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is malformed or invalid
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def require_auth(fn):
    """
    Decorator to require authentication for protected routes
    
    This decorator:
    1. Extracts JWT token from Authorization header
    2. Validates the token format and signature
    3. Injects user information into Flask's g object
    4. Allows the protected function to run if authentication succeeds
    5. Returns error response if authentication fails
    
    Usage:
        @app.route('/protected-endpoint')
        @require_auth
        def my_protected_function():
            user_id = g.user_id  # Available after successful auth
            return f"Hello {g.user_name}!"
    
    Args:
        fn: The Flask route function to protect
    
    Returns:
        function: Wrapped function with authentication check
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # STEP 1: Extract Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            return jsonify({"message": "Missing Authorization header"}), 401
        
        # STEP 2: Validate header format (should be "Bearer <token>")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "message": "Invalid Authorization header format. Use: Bearer <token>"
            }), 401
        
        token = parts[1]
        
        # STEP 3: Decode and validate JWT token
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": f"Token validation error: {str(e)}"}), 401

        # STEP 4: Validate token payload contains required user_id
        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({"message": "Invalid token payload - missing user_id"}), 401

        # STEP 5: Inject user information into Flask's g object
        # This makes user data available throughout the request lifecycle
        g.user_id = user_id                    # Primary user identifier
        g.user_email = payload.get("email")    # User's email address
        g.user_name = payload.get("name")      # User's full name
        g.user = payload                       # Full token payload for advanced use
        
        # STEP 6: Call the original protected function
        return fn(*args, **kwargs)
    
    return wrapper

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
How to Use @require_auth Decorator:

1. PROTECT A ROUTE:
   @app.route('/my-endpoint')
   @require_auth  # Add this decorator
   def my_function():
       user_id = g.user_id  # Access authenticated user's ID
       return {"message": f"Hello user {user_id}"}

2. ACCESS USER DATA:
   After @require_auth, these are available in your function:
   - g.user_id: Unique user identifier
   - g.user_email: User's email address
   - g.user_name: User's full name
   - g.user: Complete token payload

3. FRONTEND REQUIREMENTS:
   Frontend must send requests with Authorization header:
   headers: {
       'Authorization': 'Bearer ' + localStorage.getItem('token')
   }

4. ERROR RESPONSES:
   - 401: Missing/invalid/expired token
   - Token errors are automatically handled and returned as JSON

5. TESTING PROTECTED ROUTES:
   - First login to get a token
   - Include token in Authorization header for subsequent requests
   - Token expires after 7 days (configured in auth_service.py)

Next Steps for Session Management:
- Add user_id to file upload tables as foreign key
- Filter all user data queries by g.user_id
- Implement user-specific dashboards and file lists
- Add session logging and analytics
"""
