from flask import request, jsonify
from services.auth_service import create_user, authenticate_user, verify_jwt_token, delete_user_account

def signup():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not email or not name or not password:
        return jsonify({"error": "Missing fields"}), 400

    result = create_user(email, name, password)
    if result["status"] == "success":
        return jsonify(result), 201
    else:
        return jsonify(result), 400

def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    result = authenticate_user(email, password)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 401

def delete_account():
    """Delete user account endpoint"""
    try:
        # Get JWT token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify the token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get('user_id')
        
        # Delete the user account
        result = delete_user_account(user_id)
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
