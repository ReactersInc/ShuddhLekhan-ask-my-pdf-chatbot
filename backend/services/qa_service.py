import os
from flask import abort
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain  # Correct import
from langchain.prompts import PromptTemplate
from services.llm import get_gemini_flash_llm

PERSIST_ROOT = "vector_store"

# This prompt is not required, we are using "refined chain-type" , 
# which internally makes the Required Two prompts if not provided by us , 
# to give a finer and better answer based on the context

# Initial Prompt: Used for the first chunk of documents to generate an initial answer.
# Refine Prompt: Used for all subsequent chunks to refine or update that answer.

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent AI. Use the context to infer the best possible answer, even if it's not explicitly stated.

Steps:
1. Understand the question.
2. Identify relevant context facts.
3. Make logical inferences.
4. Answer clearly.

Context:
{context}

Question:
{question}

Answer:
"""
)

def answer_question_from_pdf(pdf_name: str, question: str, top_k=6):
    safe_name = pdf_name.replace("\\", "/")
    persist_dir = os.path.join(PERSIST_ROOT, safe_name)
    if not os.path.isdir(persist_dir):
        abort(400, description=f"No vector store found for PDF '{pdf_name}'")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    docs = vectordb.similarity_search(
    question,
    k=top_k
    )
    if not docs:
        return "Sorry, I couldn’t find any relevant content in that document."

    print(f"[QA] Retrieved {len(docs)} docs for question '{question}'")



    llm = get_gemini_flash_llm()

    # Removed the prompt argument here
    chain = load_qa_chain(llm=llm, chain_type="refine")

    answer = chain.run(input_documents=docs, question=question)
    return answer