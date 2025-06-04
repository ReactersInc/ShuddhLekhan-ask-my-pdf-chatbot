from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from pdf_tasks import process_pdf_task
from extensions import celery

upload_bp = Blueprint("upload", __name__)
UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"

@upload_bp.route('/', methods=['POST'])
def upload_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400

    files = request.files.getlist('files')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SUMMARY_FOLDER, exist_ok=True)

    responses = []
    for file_in in files:
        filename = secure_filename(file_in.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file_in.save(save_path)

        base_name = os.path.splitext(filename)[0]
        task = process_pdf_task.delay(filename, save_path, base_name)

        responses.append({
            "filename": filename,
            "status": "queued",
            "task_id": task.id
        })

    return jsonify(responses), 202

@upload_bp.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = celery.AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({"status": "pending"})

    elif task.state == 'SUCCESS':
        result = task.result or {}
        return jsonify({
            "status": "completed",
            "filename": result.get("filename"),
            "summary": result.get("summary_text"),
            "summary_path": result.get("summary_path"),
        })

    elif task.state == 'FAILURE':
        return jsonify({
            "status": "failed",
            "error": str(task.result)
        })

    else:
        return jsonify({"status": task.state.lower()})
