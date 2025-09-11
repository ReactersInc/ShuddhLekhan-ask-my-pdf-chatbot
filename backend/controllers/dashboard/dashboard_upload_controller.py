from flask import request, jsonify, g
from services.upload_service import save_uploaded_file
from services.folder_tree_service import build_folder_tree
from celery_tasks.embed_pdf_task import embed_pdf_task
import os

def handle_dashboard_upload():
    """
    Handle dashboard upload with user-specific session management
    """
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400

    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400

    user_id = getattr(g, 'user_id', None)  # Get user_id from auth decorator
    uploaded_files = []
    results = []

    for file_in in files:
        if file_in.filename == '':
            continue

        # Use user-specific upload if authenticated
        if user_id:
            file_info = save_uploaded_file(file_in, user_id)
            filename = file_info['filename']
            relative_path = file_info['file_path']
            filepath = file_info['absolute_path']
            base_name = os.path.splitext(filename)[0]
            
            task = embed_pdf_task.apply_async(args=[filename, filepath, base_name, relative_path])
            uploaded_files.append({
                "file_id": file_info['file_id'],
                "filename": filename,
                "original_filename": file_info['original_filename'],
                "relative_path": relative_path,
                "task_id": task.id,
                "user_specific": True
            })
        else:
            # Legacy upload for non-authenticated users
            relative_path = save_uploaded_file(file_in)
            filename = os.path.basename(relative_path)
            filepath = os.path.join("uploads", relative_path)
            base_name = os.path.splitext(filename)[0]

            task = embed_pdf_task.apply_async(args=[filename, filepath, base_name, relative_path])
            uploaded_files.append({
                "filename": filename,
                "relative_path": relative_path,
                "task_id": task.id,
                "user_specific": False
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

    # Build appropriate folder tree
    if user_id:
        # Build user-specific folder tree
        folder_tree = build_user_folder_tree(user_id)
    else:
        # Legacy folder tree
        folder_tree = build_folder_tree()

    response_data = {
        "message": "All embeddings completed",
        "uploaded_files": uploaded_files,
        "folder_tree": folder_tree,
        "user_authenticated": bool(user_id)
    }
    
    if user_id:
        response_data["user_id"] = user_id

    return jsonify(response_data), 200

def build_user_folder_tree(user_id):
    """
    Build simple file list for authenticated user (no folder wrapping)
    """
    try:
        from services.upload_service import get_user_files
        
        user_files = get_user_files(user_id)
        
        # Return simple list of files (no folder structure)
        files_list = []
        for file_record in user_files:
            file_node = {
                "id": file_record['id'],
                "name": file_record['original_filename'],
                "type": "file",
                "file_id": file_record['id'],
                "file_path": file_record['file_path'],
                "file_size": file_record['file_size'],
                "uploaded_at": file_record['uploaded_at']
            }
            files_list.append(file_node)
        
        return files_list
        
    except Exception as e:
        print(f"Error building user file list: {str(e)}")
        return build_folder_tree()  # Fallback to legacy

# some immdiate improvements needs

# need to add per-file progress updates via WebSockets
# store meta-data of embedding in DB or Redis
# also need to add RETRY TO CELERY WORKERs
