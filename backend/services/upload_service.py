import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(file):

    # This is the full relative path from user's local folder
    original_relative_path = file.filename

    path_components = original_relative_path.split('/')
    sanitized_components = [secure_filename(part) for part in path_components]
    safe_relative_path = os.path.join(*sanitized_components)

    # Saving the Uploaded files or Folders in the UPLOAD Directory
    absolute_save_path = os.path.join(UPLOAD_FOLDER, safe_relative_path)
    os.makedirs(os.path.dirname(absolute_save_path), exist_ok=True)
    file.save(absolute_save_path)

    return safe_relative_path
