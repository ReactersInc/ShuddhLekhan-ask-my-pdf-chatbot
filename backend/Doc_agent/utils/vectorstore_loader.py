import os
from langchain_community.vectorstores import FAISS
from global_models import get_embedding_model

VECTOR_DIR = "vector_store"

def load_vectorstore_from_path(path: str):
    embedding_model= get_embedding_model()

    return FAISS.load_local(path , embeddings=embedding_model, allow_dangerous_deserialization=True)

def get_all_vector_dirs_in_folder(folder_path: str):
    vector_dirs = []
    for root, dirs, files in os.walk(os.path.join(VECTOR_DIR, folder_path)):
        if "index.faiss" in files and "index.pkl" in files:
            vector_dirs.append(root)
    return vector_dirs