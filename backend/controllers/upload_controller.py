from flask import jsonify
from services.upload_service import save_uploaded_file
from services.folder_tree_service import build_folder_tree
from extensions import celery

def handle_upload_pdfs(request):
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400

    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400

    saved_files = []
    for file_in in files:
        if file_in.filename == '':
            continue
        rel_path = save_uploaded_file(file_in)
        saved_files.append(rel_path)

    folder_tree = build_folder_tree()

    return jsonify({
        "uploaded_files": saved_files,
        "folder_tree": folder_tree          
        }),200


def check_task_status(task_id):
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
