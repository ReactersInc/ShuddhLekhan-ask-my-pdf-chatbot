import os
from huggingface_hub import InferenceClient

HF_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)

def get_query_embedding(text: str) -> list[float]:
    try:
        return client.feature_extraction(text)
    except Exception as e:
        print('failed Hugging Face API')
        raise RuntimeError(f"Failed to embed query using HF API: {str(e)}")
    