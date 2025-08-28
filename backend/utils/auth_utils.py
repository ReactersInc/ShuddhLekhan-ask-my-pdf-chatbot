"""
Authentication utilities for JWT token handling and route protection
"""
from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
JWT_ALGORITHM = "HS256"

def decode_jwt(token: str):
    """Decode JWT token"""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def require_auth(fn):
    """Decorator to require authentication for protected routes"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            return jsonify({"message": "Missing Authorization header"}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Invalid Authorization header format. Use: Bearer <token>"}), 401
        
        token = parts[1]
        
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": f"Token validation error: {str(e)}"}), 401

        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({"message": "Invalid token payload - missing user_id"}), 401

        # Attach user info to flask.g for use in route handlers
        g.user_id = user_id
        g.user_email = payload.get("email")
        g.user_name = payload.get("name")
        g.user = payload  # Full payload available
        
        return fn(*args, **kwargs)
    return wrapper
