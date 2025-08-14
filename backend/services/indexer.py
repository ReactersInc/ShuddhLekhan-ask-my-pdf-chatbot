import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
from langchain.docstore.document import Document
from transformers import AutoTokenizer

PERSIST_ROOT = "vector_store"
VECTOR_STORE_TYPE = "faiss"  # or "chroma"

# Load tokenizer once
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def count_tokens(text):
    return len(tokenizer.encode(text, add_special_tokens=False))

def index_pdf_text(pdf_name: str, full_text: str, embedding_model, relative_path=None):
    splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=200 ,separators=["\n\n", "\n", ".", " ", ""], )
    chunks = splitter.split_text(full_text)

    docs = []
    total_tokens = 0

    for chunk in chunks:
        tokens = count_tokens(chunk)
        total_tokens += tokens
        docs.append(Document(
            page_content=chunk,
            metadata={
                "source": pdf_name,
                "tokens": tokens
            }
        ))

    # Create persist directory path
    if relative_path:
        path_without_ext = os.path.splitext(relative_path)[0]
        vector_rel_path = os.path.normpath(path_without_ext)
        persist_dir = os.path.join(PERSIST_ROOT, vector_rel_path)
    else:
        persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    os.makedirs(persist_dir, exist_ok=True)

    # text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(full_text)
    text_docs = [Document(page_content=chunk, metadata={"source": pdf_name, "type": "text"}) for chunk in chunks]

    # Save vector store
    if VECTOR_STORE_TYPE == "faiss":
        faiss_db = FAISS.from_documents(docs, embedding_model)
        faiss_db.save_local(persist_dir)
    elif VECTOR_STORE_TYPE == "chroma":
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
    else:
        raise ValueError("Unsupported vector store type: " + VECTOR_STORE_TYPE)

    # Save metadata.json
    metadata = {
        "pdf_name": pdf_name,
        "total_tokens": total_tokens,
        "num_chunks": len(docs)
    }
    with open(os.path.join(persist_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f)

    return True
