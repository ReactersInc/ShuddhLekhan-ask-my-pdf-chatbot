# routes/auth_routes.py
from flask import Blueprint
from controllers.auth_controller import signup, login

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

auth_bp.route("/signup", methods=["POST"])(signup)
auth_bp.route("/login", methods=["POST"])(login)
