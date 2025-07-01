from flask import Blueprint
from controllers.dashboard.dashboard_upload_controller import handle_dashboard_upload

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/upload", methods=["POST"])
def dashboard_upload():
    return handle_dashboard_upload()
