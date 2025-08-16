from sentence_transformers import SentenceTransformer, util
import numpy as np

_model = None

def get_model(model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", convert_to_tensor: bool = True):
    model = get_model(model_name)
    return model.encode(list(texts), convert_to_tensor=convert_to_tensor)

def bert_cosine_similarity(text_a: str, text_b: str, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> float:
    model = get_model(model_name)
    emb = model.encode([text_a, text_b], convert_to_tensor=True)
    sim = util.cos_sim(emb[0], emb[1]).cpu().item()
    return float(sim)

def pairwise_similarity_matrix(texts, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    model = get_model(model_name)
    emb = model.encode(list(texts), convert_to_tensor=True)
    mat = util.cos_sim(emb, emb).cpu().numpy()
    return mat
