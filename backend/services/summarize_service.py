import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.summarize import load_summarize_chain
from services.llm import get_gemini_flash_llm

PERSIST_ROOT = "vector_store"

def summarize_from_indexed_pdf(pdf_name, query=None, top_k=5):
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Loading persisted vector store
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # Always use similarity search with limited top_k chunks
    docs = vectordb.similarity_search(query or "", k=top_k)

    llm = get_gemini_flash_llm()

    chain = load_summarize_chain(llm, chain_type="stuff")

    summary = chain.run(docs)

    return summary
