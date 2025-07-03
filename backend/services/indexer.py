import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
from langchain.docstore.document import Document

PERSIST_ROOT = "vector_store"

# Switch between "faiss" or "chroma" here
VECTOR_STORE_TYPE = "faiss"  # Change to "chroma" when needed

def index_pdf_text(pdf_name: str, full_text: str, embedding_model, relative_path=None):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(full_text)

    docs = [Document(page_content=chunk, metadata={"source": pdf_name}) for chunk in chunks]

    # Create persist directory path
    if relative_path:
        path_without_ext = os.path.splitext(relative_path)[0]
        vector_rel_path = os.path.normpath(path_without_ext)
        persist_dir = os.path.join(PERSIST_ROOT, vector_rel_path)
    else:
        persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    os.makedirs(persist_dir, exist_ok=True)

    if VECTOR_STORE_TYPE == "faiss":
        faiss_db = FAISS.from_documents(documents=docs, embedding=embedding_model)
        faiss_db.save_local(persist_dir)
        
    elif VECTOR_STORE_TYPE == "chroma":
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
    else:
        raise ValueError("Unsupported vector store type: " + VECTOR_STORE_TYPE)

    return True
