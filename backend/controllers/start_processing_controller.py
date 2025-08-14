from flask import jsonify
<<<<<<< HEAD
from pdf_tasks import process_pdf_task, process_pdf_task_agentic
from services.task_router import TaskRouter
=======
from celery_tasks.process_pdf_tasks import process_pdf_task
>>>>>>> 888e8f66d4df950616db023e2b4bf9ebc7ce98c1
import os

UPLOAD_FOLDER = "uploads"

def start_processing():
    responses = []
    router = TaskRouter()

    # Walk through all uploaded files recursively
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue  # skip non-PDFs

            abs_path = os.path.join(root, fname)
            relative_path = os.path.relpath(abs_path, start=UPLOAD_FOLDER)
            file_stem = os.path.splitext(fname)[0]

            # Determine processing method using smart router
            use_agentic = router.should_use_agentic(relative_path)
            
            if use_agentic:
                task = process_pdf_task_agentic.delay(
                    filename=fname,
                    filepath=abs_path,
                    base_name=file_stem,
                    relative_path=relative_path
                )
                processing_method = "agentic"
            else:
                task = process_pdf_task.delay(
                    filename=fname,
                    filepath=abs_path,
                    base_name=file_stem,
                    relative_path=relative_path
                )
                processing_method = "standard"

            responses.append({
                "filename": relative_path,
                "task_id": task.id,
                "status": "queued",
                "processing_method": processing_method
            })

    if not responses:
        return jsonify({"error": "No PDF files found in upload directory"}), 400

    return jsonify(responses), 202
