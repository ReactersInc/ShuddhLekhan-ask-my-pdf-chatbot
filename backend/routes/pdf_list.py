from flask import Blueprint, jsonify
import os

list_bp = Blueprint('pdf_list', __name__)

UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"

@list_bp.route("/", methods=["GET"])
def list_pdf():
    pdfs = []
    
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".pdf"):
            pdf_name = os.path.splitext(filename)[0]
            summary_file_path = os.path.join(SUMMARY_FOLDER, f"{pdf_name}.txt")

            summary = "summary not available"
            if os.path.exists(summary_file_path):
                with open(summary_file_path, "r") as f:
                    summary = f.read()

            pdfs.append({
                "filename": filename,
                "summary": summary
            })

    return jsonify(pdfs)
