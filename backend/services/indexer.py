import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

PERSIST_ROOT = "vector_store"

def index_pdf_text(pdf_name: str, full_text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(full_text)

    docs = [Document(page_content=chunk, metadata={"source": pdf_name}) for chunk in chunks]

    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)
    os.makedirs(persist_dir, exist_ok=True)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_dir)
    vectordb.persist()

    return True
