import os
from datetime import datetime
from flask import send_file, abort

UPLOAD_FOLDER = 'uploads'

def build_folder_tree(base_path=UPLOAD_FOLDER):
    def walk_dir(current_path):
        items = []
        for entry in sorted(os.listdir(current_path)):
            full_path = os.path.join(current_path, entry)
            rel_path = os.path.relpath(full_path, UPLOAD_FOLDER)

            if os.path.isdir(full_path):
                children = walk_dir(full_path)
                items.append({
                    "id": rel_path,
                    "name": entry,
                    "count": count_files(full_path),
                    "isExpanded": True,
                    "children": children
                })
        return items

    def count_files(path):
        return sum(
            len([f for f in files if f.endswith('.pdf')])
            for _, _, files in os.walk(path)
        )

    return walk_dir(UPLOAD_FOLDER)

def get_all_uploaded_files(base_path=UPLOAD_FOLDER):
    files_list = []
    for root , _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, UPLOAD_FOLDER)
                folder_id = os.path.dirname(rel_path) or "root"
                size = os.path.getsize(full_path)
                upload_date = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d')


                files_list.append({
                    "id": rel_path.replace('/', '_'),  # unique flat ID
                    "name": file,
                    "relative_path": rel_path,
                    "folderId": folder_id,
                    "size": f"{round(size / (1024 * 1024), 1)} MB",
                    "uploadDate": upload_date
                })
    return files_list

def get_pdf_file(relativePath):
    
    base_path = os.path.abspath(UPLOAD_FOLDER)
    requested_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, relativePath))

    # Debuggers 
    
    # print("Requested:", requested_path)
    # print("Allowed base:", base_path)

    # For Security: prevents directory traversal
    if not requested_path.startswith(base_path):
        abort(403)

    if not os.path.exists(requested_path):
        abort(404)

    return send_file(requested_path, mimetype='application/pdf')    # Uses MIME protocol