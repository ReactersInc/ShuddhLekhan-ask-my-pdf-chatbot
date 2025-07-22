from flask import Blueprint
from controllers.dashboard.document_controller import get_document_tree
from controllers.dashboard.document_controller import list_uploaded_files
from controllers.dashboard.document_controller import get_document_tree, list_uploaded_files, view_pdf_file

document_bp = Blueprint('documents', __name__)

document_bp.route('/documents/tree', methods=['GET'])(get_document_tree)
document_bp.route('/documents/list', methods=['GET'])(list_uploaded_files)
document_bp.route('/documents/view/<path:relative_path>', methods=['GET'])(view_pdf_file)

