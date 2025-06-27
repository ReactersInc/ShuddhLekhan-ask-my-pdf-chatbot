from flask import jsonify
from pdf_tasks import process_pdf_task
import os

UPLOAD_FOLDER = "uploads"

def start_processing():
    responses = []

    # Walk through all uploaded files recursively
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue  # skip non-PDFs

            abs_path = os.path.join(root, fname)
            relative_path = os.path.relpath(abs_path, start=UPLOAD_FOLDER)
            file_stem = os.path.splitext(fname)[0]

            task = process_pdf_task.delay(
                filename=fname,
                filepath=abs_path,
                base_name=file_stem,
                relative_path=relative_path
            )

            responses.append({
                "filename": relative_path,
                "task_id": task.id,
                "status": "queued"
            })

    if not responses:
        return jsonify({"error": "No PDF files found in upload directory"}), 400

    return jsonify(responses), 202
