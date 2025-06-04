from extensions import celery
from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf
import os

@celery.task()
def process_pdf_task(filename, filepath, base_name):
    try:
        text = extract_text_from_pdf(filepath)
        index_pdf_text(base_name, text)
        summary = summarize_from_indexed_pdf(base_name)

        summary_path = os.path.join("summaries", base_name + ".txt")
        os.makedirs("summaries", exist_ok=True)
        with open(summary_path, "w") as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary   # <-- include actual summary here
        }
    except Exception as e:
        return {"status": "error", "filename": filename, "error": str(e)}
