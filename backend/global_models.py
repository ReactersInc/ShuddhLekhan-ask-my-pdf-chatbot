from langchain_huggingface import HuggingFaceEmbeddings
from services.llm import get_gemini_flash_llm
import torch

_embedding_model = None
_llm_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required but not available. Aborting embedding initialization.")

        print("Loading embedding model on GPU (cuda)")
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"}
        )
    return _embedding_model

def get_llm_model():
    global _llm_model
    if _llm_model is None:
        _llm_model = get_gemini_flash_llm()
    return _llm_model
