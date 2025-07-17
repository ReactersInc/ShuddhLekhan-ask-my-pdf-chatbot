from global_models import get_embedding_model, get_llm_model, get_image_embedding_model, get_table_embedding_model
from services.parse_pdf import extract_pdf_contents
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf
from extensions import celery
import os
import csv

def encode_table_as_text(path: str) -> str:
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = ["\t".join(row) for row in reader]
    return "\n".join(rows)

@celery.task()
def process_pdf_task(filename, filepath, base_name):
    try:
        text_emb = get_embedding_model()
        table_emb = get_table_embedding_model()
        image_emb = get_image_embedding_model()
        llm_model = get_llm_model()

        contents = extract_pdf_contents(
          filepath,
          output_dir="summaries/extracted",
                )

        text   = contents["text"]
        images = contents["images"]  
        tables = contents["tables"]   
        tables_payload = [
            (os.path.basename(tbl), encode_table_as_text(tbl))
            for tbl in tables
        ]
        index_pdf_text(
            pdf_name=base_name,
            full_text=text,
            embedding_model=text_emb,
            tables=tables_payload,
            images=images,
            table_embedding_model=table_emb,
            image_embedding_model=image_emb,
        )
        summary = summarize_from_indexed_pdf(base_name, embedding_model=text_emb, llm_model=llm_model)

        summary_path = os.path.join("summaries", base_name + ".txt")
        os.makedirs("summaries", exist_ok=True)
        with open(summary_path, "w") as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary,
            "extracted": {
                "images":  images,
                "tables":  tables,
            },
        }
    except Exception as e:
        return {"status": "error", "filename": filename, "error": str(e)}