from flask import Blueprint
from controllers.dashboard.document_controller import get_document_tree, list_uploaded_files, view_pdf_file
from utils.auth_utils import require_auth

document_bp = Blueprint('documents', __name__)

# User-specific document tree (authentication required)
@document_bp.route('/documents/tree', methods=['GET'])
@require_auth
def get_user_document_tree():
    return get_document_tree()

# User-specific document list (authentication required)
@document_bp.route('/documents/list', methods=['GET'])
@require_auth 
def get_user_document_list():
    return list_uploaded_files()

# View PDF file (authentication required)
@document_bp.route('/documents/view/<path:relative_path>', methods=['GET'])
@require_auth
def view_user_pdf_file(relative_path):
    return view_pdf_file(relative_path)

