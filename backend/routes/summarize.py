from flask import Blueprint, request, jsonify
import os

summarize_bp = Blueprint("summarize", __name__)
SUMMARY_FOLDER = "summaries"

@summarize_bp.route('/<pdf_name>', methods=['GET'])
def get_summary(pdf_name):
    base_name = os.path.splitext(pdf_name)[0]  # remove .pdf if present
    summary_path = os.path.join(SUMMARY_FOLDER, f"{base_name}.txt")

    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = f.read()
        return jsonify({"pdf": pdf_name, "summary": summary})
    else:
        return jsonify({"error": "Summary not found"}), 404
