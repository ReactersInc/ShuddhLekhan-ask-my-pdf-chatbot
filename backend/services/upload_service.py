import os
import time
from werkzeug.utils import secure_filename
from pdf_tasks import process_pdf_task

UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

def save_and_queue_file(file):

    # This is the full relative path from user's local folder
    original_relative_path = file.filename

    path_components = original_relative_path.split('/')
    sanitized_components = [secure_filename(part) for part in path_components]
    safe_relative_path = os.path.join(*sanitized_components)

    # Saving the Uploaded files or Folders in the UPLOAD Directory
    absolute_save_path = os.path.join(UPLOAD_FOLDER, safe_relative_path)
    os.makedirs(os.path.dirname(absolute_save_path), exist_ok=True)
    file.save(absolute_save_path)

    # Extracting base filename (without extension) for downstream processing
    filename_only = os.path.basename(absolute_save_path)
    file_stem = os.path.splitext(filename_only)[0]

    task = process_pdf_task.delay(
        filename = filename_only,
        filepath = absolute_save_path,
        base_name = file_stem,
        relative_path=safe_relative_path
    )

    return task, safe_relative_path
