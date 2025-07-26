from flask import Blueprint, jsonify
from services.auth_decorator import auth_required

protected_bp = Blueprint("protected_bp", __name__)

@protected_bp.route('/profile', methods=['GET'])
@auth_required
def user_profile():
    return jsonify({"message": "Welcome to the protected AI Agent Module!"})