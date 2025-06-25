import os
import time
from werkzeug.utils import secure_filename
from pdf_tasks import process_pdf_task

UPLOAD_FOLDER = "uploads"
SUMMARY_FOLDER = "summaries"
DELAY_BETWEEN_TASKS = 5

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

def save_and_queue_file(file):
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    base_name = os.path.splitext(filename)[0]
    task = process_pdf_task.delay(filename, save_path, base_name)

    # Optional: avoid rate limits
    time.sleep(DELAY_BETWEEN_TASKS)

    return task, filename
