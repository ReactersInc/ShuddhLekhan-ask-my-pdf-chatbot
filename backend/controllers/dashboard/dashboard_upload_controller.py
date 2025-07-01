from flask import request, jsonify
from services.upload_service import save_uploaded_file
from services.folder_tree_service import build_folder_tree
from celery_tasks.embed_pdf_task import embed_pdf_task
import os

def handle_dashboard_upload():
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400

    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400

    uploaded_files = []
    results = []

    for file_in in files:
        if file_in.filename == '':
            continue

        relative_path = save_uploaded_file(file_in)
        filename = os.path.basename(relative_path)
        filepath = os.path.join("uploads", relative_path)
        base_name = os.path.splitext(filename)[0]

        task = embed_pdf_task.apply_async(args=[filename, filepath, base_name, relative_path])
        uploaded_files.append({
            "filename": filename,
            "relative_path": relative_path,
            "task_id": task.id
        })

    # Wait for all embeddings to complete
    for file in uploaded_files:
        try:
            task_result = embed_pdf_task.AsyncResult(file["task_id"]).get(timeout=180)  # 3 mins per file
            file["status"] = task_result.get("status", "unknown")
            file["message"] = task_result.get("message", "")
        except Exception as e:
            file["status"] = "error"
            file["error"] = str(e)

    folder_tree = build_folder_tree()

    return jsonify({
        "message": "All embeddings completed",
        "uploaded_files": uploaded_files,
        "folder_tree": folder_tree
    }), 200


# some immdiate improvements needs

# need to add per-file progress updates via WebSockets
# store meta-data of embedding in DB or Redis
# also need to add RETRY TO CELERY WORKERs
