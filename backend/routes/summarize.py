from flask import Blueprint, request, jsonify
import os

from services.parse_pdf import extract_text_from_pdf
from services.summarize_service import generate_summary, save_summary

summarize_bp = Blueprint("summarize", __name__)
UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"

@summarize_bp.route('/<pdf_name>', methods=['GET', 'POST'])
def summarize_pdf(pdf_name):
    base_name = os.path.splitext(pdf_name)[0]  # strip .pdf if sent
    summary_path = os.path.join(SUMMARY_FOLDER, f"{base_name}.txt")
    
    # On GET: retrieve existing summary if available
    if request.method == "GET":
        if os.path.exists(summary_path):
            with open(summary_path, "r") as f:
                summary = f.read()
            return jsonify({"pdf": pdf_name, "summary": summary})
        else:
            return jsonify({"error": "Summary not found"}), 404
    
    # On POST: generate new summary
    elif request.method == "POST":
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not found"}), 404
        
        try:
            text = extract_text_from_pdf(pdf_path)
            summary = generate_summary(text)
            save_summary(summary, base_name)
            return jsonify({"pdf": pdf_name, "summary": summary})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
