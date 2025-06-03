from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

PERSIST_ROOT = "vector_store"

def index_pdf_text(pdf_name: str , full_text: str):
    
    #splitting text
    splitter = RecursiveCharacterTextSplitter(chuck_size = 1000 , chunk_overlap=200)
    chunks = splitter.split_text(full_text)

    #Wrapping as LangChain Documents
    docs = [Document(page_content=chunk, metadata={"source": pdf_name}) for chunk in chunks]


    # Create unique persist directory
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)
    os.makedirs(persist_dir, exist_ok=True)

    # Embed and store in ChromaDB
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_dir)
    vectordb.persist()

    return True
