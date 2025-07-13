import jwt
from flask import request, jsonify, current_app
from functools import wraps

def verify_jwt(token):
    try:
        secret = current_app.config["SUPABASE_JWT_SECRET"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Authorization token is missing or malformed"}), 401

        token = token.split(" ")[1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 403

        return f(*args, **kwargs)
    return wrapper