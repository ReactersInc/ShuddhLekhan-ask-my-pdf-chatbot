from langchain_huggingface import HuggingFaceEmbeddings
from services.llm import get_gemma_llm
from celery.signals import worker_process_init
import torch
import uuid
_MODEL_INSTANCE_ID = uuid.uuid4()


_embedding_model = None
_llm_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required but not available. Aborting embedding initialization.")

        print(f" Loading embedding model [{_MODEL_INSTANCE_ID}] on GPU (cuda)")
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cuda"}
        )
    else:
        print(f" Reusing embedding model [{_MODEL_INSTANCE_ID}]")
    return _embedding_model

def get_llm_model():
    global _llm_model
    if _llm_model is None:
        _llm_model = get_gemma_llm()
    return _llm_model

@worker_process_init.connect
def preload_models(**kwargs):
    print("🔥 Preloading embedding model once at worker startup")
    get_embedding_model()