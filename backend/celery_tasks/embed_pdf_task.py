from global_models import get_embedding_model
from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from extensions import celery
import os

@celery.task()
def embed_pdf_task(filename, filepath, base_name,relative_path=None):
    try:
        embedding_model = get_embedding_model()

        text = extract_text_from_pdf(filepath)
        index_pdf_text(base_name,text,embedding_model=embedding_model)

        return{
            "status":"completed",
            "filename" : filename,
            "message": "Embedding done successfully"
        }
    
    except Exception as e :
        return {
            "status": "error",
            "filename":filename,
            "error":str(e)
        }