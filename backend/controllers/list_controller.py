from flask import jsonify
from services.list_service import get_all_pdf_with_summaries

def handle_list_pdfs():
    pdfs = get_all_pdf_with_summaries()
    return jsonify(pdfs)