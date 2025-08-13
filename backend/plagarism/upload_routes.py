"""
Purpose:
--------
Defines the Flask API route for handling plagiarism PDF uploads.
This route orchestrates the entire plagiarism-checking pipeline:
1. Receives and stores the uploaded PDF.
2. Processes the PDF into section-based chunks.
3. Extracts keywords, key phrases, and key points using LLM.
4. (Future) Initiates web scraping for related content.
5. (Future) Runs a Cython-based plagiarism checker.

Responsibilities:
-----------------
- Validate and securely store uploaded files.
- Call service layer modules for PDF processing and keyword extraction.
- Prepare JSON responses for the client.
- Manage any future pipeline steps (scraping, plagiarism detection).

Note:
-----
This route does NOT contain PDF parsing, keyword extraction, or scraping logic directly.
All heavy processing is delegated to dedicated services in `plagarism/services/`.
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os, json
from pathlib import Path

from plagarism.pdf_processor import process_pdf
from plagarism.keyword_extractor import extract_keywords_from_sections

UPLOAD_DIR = "./plagarism/uploads"
RESULT_DIR = "./plagarism/results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

plag_upload_bp = Blueprint("plagiarism_upload_bp", __name__)

@plag_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    try:
        # Step 1: Process PDF into chunks
        sections, chunks_path = process_pdf(file_path, RESULT_DIR)

        # Step 2: Extract keywords & key points
        keyword_results = extract_keywords_from_sections(sections)
        keywords_path = os.path.join(RESULT_DIR, Path(filename).stem + ".keywords.json")
        with open(keywords_path, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, indent=2, ensure_ascii=False)

        # Step 3: Future - Scraping & plagiarism checking
        # scraped_data = scrape_sources(keyword_results)
        # check_results = run_plagiarism_check(file_path, scraped_data)

        return jsonify({
            "message": "File processed successfully",
            "pdf_path": file_path,
            "chunks_json": chunks_path,
            "keywords_json": keywords_path,
            "sections_count": len(sections)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
