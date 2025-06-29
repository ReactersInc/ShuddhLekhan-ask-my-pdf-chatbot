from flask import Blueprint
from controllers.document_controller import get_document_tree
from controllers.document_controller import list_uploaded_files

document_bp = Blueprint('documents', __name__)

document_bp.route('/documents/tree', methods=['GET'])(get_document_tree)
document_bp.route('/documents/list', methods=['GET'])(list_uploaded_files)