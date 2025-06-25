from flask import Blueprint, request, jsonify
from controllers.upload_controller import handle_upload_pdfs, check_task_status

upload_bp = Blueprint("upload", __name__)

@upload_bp.route('/', methods=['POST'])
def upload_pdfs():
    return handle_upload_pdfs(request)

@upload_bp.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    return check_task_status(task_id)
