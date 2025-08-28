import bcrypt
import uuid
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# JWT Secret key - in production, use a proper secret
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

# Try to import supabase admin, but provide fallback
try:
    from database.supabase_admin import supabase_admin
    SUPABASE_AVAILABLE = True
    print("✅ Supabase admin client loaded successfully")
except Exception as e:
    print(f"⚠️ Supabase admin client failed to load: {str(e)}")
    SUPABASE_AVAILABLE = False
    supabase_admin = None

def create_user(email, name, password):
    """Create a new user using Supabase"""
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Database service unavailable"}
    
    try:
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())

        # Check if user already exists
        existing_user = supabase_admin.table('users').select('*').eq('email', email.lower()).execute()
        
        if existing_user.data:
            return {"status": "error", "message": "User with this email already exists"}
        
        # Insert new user into Supabase
        user_data = {
            "id": user_id,
            "email": email.lower(),
            "name": name,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase_admin.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            
            # Generate JWT token
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


def authenticate_user(email, password):
    """Authenticate user using Supabase"""
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Database service unavailable"}
    
    try:
        # Get user from Supabase
        result = supabase_admin.table('users').select('*').eq('email', email.lower()).execute()
        
        if not result.data:
            return {"status": "error", "message": "User not found"}

        user = result.data[0]
        
        # Verify password
        if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            # Update last login
            supabase_admin.table('users').update({
                "last_login": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
            
            # Generate JWT token
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
            return {"status": "error", "message": "Incorrect password"}
            
    except Exception as e:
        print(f"Error authenticating user: {str(e)}")
        return {"status": "error", "message": f"Database connection error: {str(e)}"}

def generate_jwt_token(user_id, email, name):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'name': name,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_id(user_id):
    """Get user by ID from Supabase"""
    try:
        result = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        
        if result.data:
            user = result.data[0]
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
    """Delete user account"""
    try:
        # Delete the user
        result = supabase_admin.table('users').delete().eq('id', user_id).execute()
        
        if result.data is not None:  # Supabase returns [] for successful delete
            return {"status": "success", "message": "Account deleted successfully"}
        else:
            return {"status": "error", "message": "Failed to delete account"}
            
    except Exception as e:
        print(f"Error deleting user account: {str(e)}")
        return {"status": "error", "message": str(e)}
