from global_models import get_embedding_model, get_llm_model
from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf
from extensions import celery
import os

@celery.task(rate_limit="15/m")
def process_pdf_task(filename, filepath, base_name):
    try:
        embedding_model = get_embedding_model()
        llm_model = get_llm_model()

        text = extract_text_from_pdf(filepath)
        index_pdf_text(base_name, text, embedding_model=embedding_model)
        summary = summarize_from_indexed_pdf(base_name, embedding_model=embedding_model, llm_model=llm_model)

        summary_path = os.path.join("summaries", base_name + ".txt")
        os.makedirs("summaries", exist_ok=True)
        with open(summary_path, "w") as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary
        }
    except Exception as e:
        return {"status": "error", "filename": filename, "error": str(e)}
