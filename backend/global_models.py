from langchain_huggingface import HuggingFaceEmbeddings
from services.llm import get_gemini_flash_llm

_embedding_model = None
_table_embedding_model = None
_image_embedding_model = None
_caption_processor = None
_caption_model = None  
_llm_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embedding_model

def get_image_embedding_model():
    global _image_embedding_model
    if _image_embedding_model is None:
        _image_embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/clip-ViT-B-32",
            encode_kwargs={"encode_method": "image"},
        )

    return _image_embedding_model


def get_llm_model():
    global _llm_model
    if _llm_model is None:
        _llm_model = get_gemini_flash_llm()
    return _llm_model


