import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from services.llm import get_gemini_flash_llm

VECTOR_ROOT = "vector_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # full huggingface model name

def get_qa_answer(pdf_name: str, question: str) -> str:
    persist_dir = os.path.join(VECTOR_ROOT, pdf_name)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = vectordb.as_retriever()

    llm = get_gemini_flash_llm()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    answer = qa_chain.run(question)
    return answer
