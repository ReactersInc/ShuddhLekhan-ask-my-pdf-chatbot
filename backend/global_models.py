from langchain_huggingface import HuggingFaceEmbeddings
from services.llm import get_gemini_flash_llm
<<<<<<< Updated upstream
=======
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
>>>>>>> Stashed changes

_embedding_model = None
_table_embedding_model = None
_image_embedding_model = None
_caption_processor = None
_caption_model = None  
_llm_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
<<<<<<< Updated upstream
        _embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
=======
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading embedding model on {device}")

        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": device}
        )
>>>>>>> Stashed changes
    return _embedding_model

def get_table_embedding_model():
    global _table_embedding_model
    if _table_embedding_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _table_embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1",
            model_kwargs={"device": device},
        )
    return _table_embedding_model

def get_image_embedding_model():
    global _image_embedding_model
    if _image_embedding_model is None:
        _image_embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/clip-ViT-B-32",
            encode_kwargs={"encode_method": "image"},
        )

    return _image_embedding_model

def get_image_captioner():
    """Return a BLIP-based image captioning processor and model."""
    global _caption_processor, _caption_model
    if _caption_processor is None or _caption_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _caption_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _caption_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(device)
    return _caption_processor, _caption_model

def get_llm_model():
    global _llm_model
    if _llm_model is None:
        _llm_model = get_gemini_flash_llm()
    return _llm_model


