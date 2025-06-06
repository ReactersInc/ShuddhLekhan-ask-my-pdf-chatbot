import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from services.llm import get_gemini_flash_llm

PERSIST_ROOT = "vector_store"

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent assistant. Based on the context provided, answer the following question as accurately as possible. If the answer cannot be found, reply "Answer not found in document."

Context:
{context}

Question:
{question}

Answer:
"""
)

def answer_question_from_pdf(pdf_name: str, question: str, top_k=4):
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    docs = vectordb.similarity_search(question, k=top_k)
    context = "\n".join([doc.page_content for doc in docs])

    llm = get_gemini_flash_llm()
    chain = LLMChain(llm=llm, prompt=QA_PROMPT)

    answer = chain.run(context=context, question=question)
    return answer
