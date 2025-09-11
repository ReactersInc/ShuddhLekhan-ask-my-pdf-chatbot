from flask import Blueprint
from controllers.dashboard.dashboard_upload_controller import handle_dashboard_upload
from utils.auth_utils import require_auth

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/upload", methods=["POST"])
@require_auth  # Add authentication requirement
def dashboard_upload():
    return handle_dashboard_upload()
