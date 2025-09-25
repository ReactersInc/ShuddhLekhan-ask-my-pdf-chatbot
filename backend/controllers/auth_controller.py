# =============================================================================
# AUTHENTICATION CONTROLLER MODULE
# =============================================================================
"""
Authentication Controller for Ask My PDF Chatbot

This module contains the HTTP request handlers for authentication operations.
It serves as the bridge between HTTP routes and authentication business logic.

Features:
- User registration (signup)
- User login with JWT token generation
- Account deletion with authentication verification
- Input validation and error handling
- Proper HTTP status codes and JSON responses

Architecture:
- Controllers receive HTTP requests and extract data
- Controllers delegate business logic to auth_service
- Controllers format responses and return appropriate status codes
- Error handling with meaningful messages for frontend

Author: [Your Team]
Created for: CDAC Project - Ask My PDF Chatbot
"""

from flask import request, jsonify
from services.auth_service import create_user, authenticate_user, verify_jwt_token, delete_user_account

def signup():
    """
    Handle user registration requests
    
    This endpoint:
    1. Extracts user data from request JSON
    2. Validates required fields are present
    3. Calls auth_service to create the user
    4. Returns success with JWT token or error message
    
    Expected Request Body:
    {
        "email": "user@example.com",
        "name": "User Name", 
        "password": "secure_password"
    }
    
    Success Response (201):
    {
        "status": "success",
        "message": "User created successfully",
        "token": "jwt_token_here",
        "user": {
            "user_id": "uuid",
            "email": "user@example.com",
            "name": "User Name"
        }
    }
    
    Error Response (400):
    {
        "error": "Missing fields" | "Email already exists" | "Database error"
    }
    """
    # STEP 1: Extract and validate request data
    data = request.get_json()
    
    # Handle case where no JSON is sent
    if not data:
        return jsonify({"error": "Request must contain JSON data"}), 400
    
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    # STEP 2: Validate all required fields are present
    if not email or not name or not password:
        return jsonify({"error": "Missing fields: email, name, and password are required"}), 400

    # STEP 3: Delegate to auth service for user creation
    result = create_user(email, name, password)
    
    # STEP 4: Return appropriate response based on result
    if result["status"] == "success":
        return jsonify(result), 201  # Created
    else:
        return jsonify(result), 400  # Bad Request

def login():
    """
    Handle user login requests
    
    This endpoint:
    1. Extracts login credentials from request
    2. Validates email and password are provided
    3. Calls auth_service to authenticate user
    4. Returns JWT token on success or error message on failure
    
    Expected Request Body:
    {
        "email": "user@example.com",
        "password": "user_password"
    }
    
    Success Response (200):
    {
        "status": "success",
        "message": "Login successful",
        "token": "jwt_token_here",
        "user": {
            "user_id": "uuid",
            "email": "user@example.com", 
            "name": "User Name"
        }
    }
    
    Error Response (401):
    {
        "status": "error",
        "message": "Invalid email or password"
    }
    """
    # STEP 1: Extract login credentials
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request must contain JSON data"}), 400
    
    email = data.get("email")
    password = data.get("password")

    # STEP 2: Validate credentials are provided
    if not email or not password:
        return jsonify({"error": "Missing fields: email and password are required"}), 400

    # STEP 3: Authenticate user via auth service
    result = authenticate_user(email, password)
    
    # STEP 4: Return success or failure response
    if result["status"] == "success":
        return jsonify(result), 200  # OK
    else:
        return jsonify(result), 401  # Unauthorized

def delete_account():
    """
    Handle account deletion requests
    
    This endpoint:
    1. Extracts JWT token from Authorization header
    2. Verifies token is valid and not expired
    3. Calls auth_service to delete user account
    4. Returns success message or error
    
    Required Headers:
    Authorization: Bearer <jwt_token>
    
    Success Response (200):
    {
        "status": "success",
        "message": "Account deleted successfully"
    }
    
    Error Responses:
    401: {"error": "Missing or invalid authorization header"}
    401: {"error": "Invalid or expired token"}
    400: {"error": "Database error message"}
    500: {"error": "Internal server error"}
    
    Security Notes:
    - Requires valid JWT token for authentication
    - User can only delete their own account
    - All user data and associated files should be cleaned up
    """
    try:
        # STEP 1: Extract JWT token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Missing or invalid authorization header. Use: Authorization: Bearer <token>"
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # STEP 2: Verify the JWT token is valid
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # STEP 3: Extract user ID from verified token
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 401
        
        # STEP 4: Delete the user account
        result = delete_user_account(user_id)
        
        # STEP 5: Return result
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
How to Use These Controllers:

1. INTEGRATE WITH ROUTES:
   from controllers.auth_controller import signup, login, delete_account
   
   app.route('/api/auth/signup', methods=['POST'])(signup)
   app.route('/api/auth/login', methods=['POST'])(login)
   app.route('/api/auth/delete-account', methods=['DELETE'])(delete_account)

2. FRONTEND INTEGRATION:
   - Send POST requests to /api/auth/signup and /api/auth/login
   - Include Authorization header for delete_account: 'Bearer ' + token
   - Handle different HTTP status codes appropriately

3. ERROR HANDLING:
   - Always check response status code
   - Display error messages from response JSON
   - Implement retry logic for network errors

4. TESTING:
   Use tools like Postman or curl:
   
   # Signup
   curl -X POST http://localhost:5000/api/auth/signup \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","name":"Test User","password":"password123"}'
   
   # Login  
   curl -X POST http://localhost:5000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"password123"}'

5. FUTURE ENHANCEMENTS:
   - Add rate limiting for signup/login attempts
   - Implement email verification before account activation
   - Add password reset functionality
   - Include user profile update endpoints
   - Add account suspension/ban capabilities for admin users
"""
