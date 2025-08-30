"""
AUTH SERVICE - Core Authentication Logic
========================================

This service handles all user authentication operations for the application.
It provides secure user registration, login, token generation, and account management.

Features Implemented:
- ✅ User registration with email validation
- ✅ Secure password hashing using bcrypt
- ✅ JWT token generation and verification
- ✅ User login with password validation
- ✅ Account deletion functionality
- ✅ Supabase database integration
- ✅ Error handling and validation

Dependencies:
- bcrypt: For secure password hashing
- PyJWT: For JWT token handling
- supabase: For database operations
- uuid: For unique user ID generation

Author: Your Name
Date: August 2025
Purpose: Authentication system for Ask My PDF Chatbot
"""

import bcrypt
import uuid
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

# JWT Secret key - IMPORTANT: Change this in production to a strong random string
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

# Try to import supabase admin client with fallback for development
try:
    from database.supabase_admin import supabase_admin
    SUPABASE_AVAILABLE = True
    print("✅ Supabase admin client loaded successfully")
except Exception as e:
    print(f"⚠️ Supabase admin client failed to load: {str(e)}")
    SUPABASE_AVAILABLE = False
    supabase_admin = None

# =============================================================================
# USER REGISTRATION FUNCTION
# =============================================================================

def create_user(email, name, password):
    """
    Create a new user account with secure password hashing
    
    Process:
    1. Check if database is available
    2. Hash the password using bcrypt (industry standard)
    3. Generate unique user ID using UUID4
    4. Check if email already exists in database
    5. Insert new user record into Supabase 'users' table
    6. Generate JWT token for immediate login
    7. Return success response with user data and token
    
    Args:
        email (str): User's email address (will be converted to lowercase)
        name (str): User's full name
        password (str): User's password (will be hashed before storage)
    
    Returns:
        dict: Response with status, message, user data, and JWT token
    """
    # Check if database connection is available
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Database service unavailable"}
    
    try:
        # STEP 1: Hash password using bcrypt (salt is automatically generated)
        # bcrypt automatically generates a unique salt for each password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # STEP 2: Generate unique user ID using UUID4
        user_id = str(uuid.uuid4())

        # STEP 3: Check if user already exists (email uniqueness)
        existing_user = supabase_admin.table('users').select('*').eq('email', email.lower()).execute()
        
        if existing_user.data:
            return {"status": "error", "message": "User with this email already exists"}
        
        # STEP 4: Prepare user data for database insertion
        user_data = {
            "id": user_id,
            "email": email.lower(),  # Store email in lowercase for consistency
            "name": name,
            "password_hash": password_hash,  # Store hashed password, never plain text
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # STEP 5: Insert new user into Supabase database
        result = supabase_admin.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            
            # STEP 6: Generate JWT token for immediate login after registration
            token = generate_jwt_token(user_id, email.lower(), name)
            
            return {
                "status": "success", 
                "message": "User created successfully",
                "user": {
                    "id": user_id,
                    "email": email.lower(),
                    "name": name
                },
                "token": token
            }
        else:
            return {"status": "error", "message": "Failed to create user"}
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return {"status": "error", "message": f"Database connection error: {str(e)}"}


# =============================================================================
# USER LOGIN FUNCTION
# =============================================================================

def authenticate_user(email, password):
    """
    Authenticate user login with email and password
    
    Process:
    1. Check if database is available
    2. Find user by email in database
    3. Verify password against stored hash using bcrypt
    4. Update last login timestamp
    5. Generate new JWT token for session
    6. Return success response with user data and token
    
    Args:
        email (str): User's email address
        password (str): User's password (plain text, will be verified against hash)
    
    Returns:
        dict: Response with status, message, user data, and JWT token
    """
    # Check if database connection is available
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Database service unavailable"}
    
    try:
        # STEP 1: Find user by email in database
        result = supabase_admin.table('users').select('*').eq('email', email.lower()).execute()
        
        if not result.data:
            return {"status": "error", "message": "User not found"}

        user = result.data[0]
        
        # STEP 2: Verify password using bcrypt
        # bcrypt.checkpw() safely compares the plain password with the hashed version
        if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            
            # STEP 3: Update last login timestamp (for analytics/security)
            supabase_admin.table('users').update({
                "last_login": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
            
            # STEP 4: Generate new JWT token for this session
            token = generate_jwt_token(user['id'], user['email'], user['name'])
            
            return {
                "status": "success", 
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "name": user['name']
                },
                "token": token
            }
        else:
            # Password doesn't match
            return {"status": "error", "message": "Incorrect password"}
            
    except Exception as e:
        print(f"Error authenticating user: {str(e)}")
        return {"status": "error", "message": f"Database connection error: {str(e)}"}

# =============================================================================
# JWT TOKEN FUNCTIONS
# =============================================================================

def generate_jwt_token(user_id, email, name):
    """
    Generate JWT token for user authentication
    
    JWT (JSON Web Token) is a secure way to transmit user identity between client and server.
    The token contains user information and has an expiration date for security.
    
    Token Structure:
    - Header: Contains algorithm info (HS256)
    - Payload: Contains user data (user_id, email, name, expiration)
    - Signature: Ensures token hasn't been tampered with
    
    Args:
        user_id (str): Unique user identifier
        email (str): User's email address
        name (str): User's full name
    
    Returns:
        str: Encoded JWT token string
    """
    payload = {
        'user_id': user_id,        # Primary identifier for the user
        'email': email,            # User's email (useful for display)
        'name': name,              # User's name (useful for display)
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()   # Issued at timestamp
    }
    # Encode the payload using our secret key and HS256 algorithm
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """
    Verify and decode JWT token
    
    This function validates that:
    1. Token is properly formatted
    2. Token hasn't expired
    3. Token signature is valid (hasn't been tampered with)
    
    Args:
        token (str): JWT token string to verify
    
    Returns:
        dict|None: Decoded payload if valid, None if invalid/expired
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid (malformed or wrong signature)
        return None

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_user_by_id(user_id):
    """
    Retrieve user information by user ID
    
    This function is useful for getting user details when you have their ID
    (for example, from a JWT token payload).
    
    Args:
        user_id (str): Unique user identifier
    
    Returns:
        dict|None: User information if found, None if not found
    """
    try:
        result = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        
        if result.data:
            user = result.data[0]
            # Return safe user data (no password hash)
            return {
                "id": user["id"],
                "email": user["email"], 
                "name": user["name"],
                "created_at": user["created_at"],
                "last_login": user.get("last_login")
            }
        return None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def delete_user_account(user_id):
    """
    Delete user account permanently
    
    WARNING: This action is irreversible!
    This function will remove the user and all associated data.
    
    For future development: You may want to add soft deletion
    or data retention policies before implementing hard deletion.
    
    Args:
        user_id (str): Unique user identifier to delete
    
    Returns:
        dict: Response with status and message
    """
    try:
        # Delete the user record from database
        result = supabase_admin.table('users').delete().eq('id', user_id).execute()
        
        # Supabase returns empty list [] for successful deletion
        if result.data is not None:
            return {"status": "success", "message": "Account deleted successfully"}
        else:
            return {"status": "error", "message": "Failed to delete account"}
            
    except Exception as e:
        print(f"Error deleting user account: {str(e)}")
        return {"status": "error", "message": str(e)}

# =============================================================================
# NOTES FOR FUTURE DEVELOPMENT
# =============================================================================
"""
TODO: Session Management Features to Add

1. USER-SPECIFIC FILE UPLOADS:
   - Add user_id to file upload tables
   - Filter file lists by current user
   - Ensure users can only see their own files

2. SESSION TRACKING:
   - Track user sessions with login/logout times
   - Implement session timeout
   - Add "Remember me" functionality

3. PASSWORD MANAGEMENT:
   - Password reset via email
   - Password change functionality
   - Password strength validation

4. USER PROFILES:
   - Edit profile information
   - Upload profile pictures
   - User preferences/settings

5. SECURITY ENHANCEMENTS:
   - Rate limiting for login attempts
   - Email verification for new accounts
   - Two-factor authentication (2FA)
   - Audit logs for security events

6. ADMIN FEATURES:
   - User management dashboard
   - Usage analytics
   - Account suspension/activation

Starting Point for Session Implementation:
- Use the @require_auth decorator in utils/auth_utils.py
- Add user_id foreign keys to relevant tables
- Update upload/list endpoints to use g.user_id from JWT
- Test with different user accounts to ensure isolation
"""
