from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import traceback

from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf  # <-- new function

upload_bp = Blueprint("upload", __name__)
UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"

@upload_bp.route('/', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400

    file_in = request.files['file']
    if file_in.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file_in.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SUMMARY_FOLDER, exist_ok=True)

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file_in.save(save_path)

    try:
        base_name = os.path.splitext(filename)[0]

        # Extracting text from PDF
        text = extract_text_from_pdf(save_path)

        # Step 1: Indexing the PDF text chunks for retrieval
        index_pdf_text(base_name, text)

        # Step 2: Summarize using indexed chunks
        summary = summarize_from_indexed_pdf(base_name)

        # Saving summary to disk
        with open(os.path.join(SUMMARY_FOLDER, base_name + ".txt"), "w") as f:
            f.write(summary)

        return jsonify({
            "message": f"{filename} uploaded, indexed, and summarized successfully",
            "filename": filename,
            "summary": summary
        }), 200

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error during summarization:\n{tb}")
        return jsonify({
            "message": f"{filename} uploaded, but summarization failed",
            "filename": filename,
            "error": str(e)
        }), 500
