from flask import request, jsonify
from services.auth_service import create_user, authenticate_user

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