from flask import Blueprint
from controllers.list_controller import handle_list_pdfs

list_bp = Blueprint('pdf_list', __name__)

@list_bp.route("/", methods=["GET"])
def list_pdf():
    return handle_list_pdfs()