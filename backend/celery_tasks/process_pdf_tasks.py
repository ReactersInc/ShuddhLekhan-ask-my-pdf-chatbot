import time
from global_models import get_embedding_model, get_llm_model
from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf
from extensions import celery
import os

@celery.task(rate_limit="30/m")
def process_pdf_task(filename, filepath, base_name, relative_path=None):
    try:
        embedding_model = get_embedding_model()
        llm_model = get_llm_model()

        full_start = time.time()

        # Step 1: Extract text
        t0 = time.time()
        text = extract_text_from_pdf(filepath)
        t1 = time.time()

        # Step 2: Indexing
        index_pdf_text(base_name, text, embedding_model=embedding_model)
        t2 = time.time()

        # Step 3: Summarization
        summary = summarize_from_indexed_pdf(base_name, embedding_model=embedding_model, llm_model=llm_model)
        t3 = time.time()

        # Save timings
        extract_time = round(t1 - t0, 2)
        index_time = round(t2 - t1, 2)
        summary_time = round(t3 - t2, 2)
        total_time = round(t3 - full_start, 2)

        # Log to file
        timing_log_dir = "timing_logs"
        os.makedirs(timing_log_dir, exist_ok=True)
        timing_log_path = os.path.join(timing_log_dir, f"{base_name}_timing.txt")

        with open(timing_log_path, "w") as f:
            f.write(f"Text Extraction: {extract_time} sec\n")
            f.write(f"Indexing:        {index_time} sec\n")
            f.write(f"Summarization:   {summary_time} sec\n")
            f.write(f"-----------------------------\n")
            f.write(f"Total:           {total_time} sec\n")

        # Save summary
        if relative_path:
            summary_rel_path = os.path.splitext(relative_path)[0] + ".txt"
            summary_path = os.path.join("summaries", summary_rel_path)
        else:
            summary_path = os.path.join("summaries", base_name + ".txt")

        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, "w") as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary,
            "time_taken": {
                "extraction": extract_time,
                "indexing": index_time,
                "summarization": summary_time,
                "total": total_time
            }
        }

    except Exception as e:
        return {"status": "error", "filename": filename, "error": str(e)}
