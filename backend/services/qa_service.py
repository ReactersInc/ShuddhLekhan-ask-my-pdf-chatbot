import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.chains.combine_documents import create_stuff_documents_chain
from services.llm import get_gemma_llm

PERSIST_ROOT = "vector_store/exascale"

QA_PROMPT = PromptTemplate(
    input_variables=["input_documents", "question"],
    template="""
You are an intelligent and helpful AI assistant.

Use the following input documents to answer the user's question as clearly and informatively as possible. 
You are allowed to **explain, summarize, infer, and reason** — but only using information found in the input documents. Do not use outside knowledge or make assumptions.

If the documents do **not** contain enough information to answer the question, respond **exactly** with:
    NOT FOUND IN DOCUMENT

Your job:
- Carefully read the documents.
- Understand what the user is asking.
- Extract relevant details.
- Explain the answer in simple, clear language.
- If unsure, do not guess — return: NOT FOUND IN DOCUMENT

---

Input Documents:
{input_documents}

Question:
{question}

Answer:
"""
)

def is_not_in_doc(answer: str) -> bool:
    return answer.strip().upper() == "NOT FOUND IN DOCUMENT"


def answer_question_from_pdf(pdf_name: str, question: str, top_k=6):
    pdf_name = os.path.splitext(pdf_name)[0]
    persist_path = os.path.join(PERSIST_ROOT, pdf_name)

    if not os.path.exists(persist_path):
        raise ValueError(f"No vector index found for: {pdf_name}")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.load_local(
        persist_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = vectordb.similarity_search(question, k=top_k)

    if not docs:
        return "Sorry, no relevant content was found in this document."

    llm = get_gemma_llm()

    # Build the chain using latest composable APIs
    chain = create_stuff_documents_chain(
        llm=llm,
        prompt=QA_PROMPT,
        document_variable_name="input_documents"
    )

    # Step 1: Try document-based QA
    response = chain.invoke({
        "input_documents": docs,
        "question": question
    })

    # Step 2: Fallback to general LLM knowledge if not found
    if is_not_in_doc(response if isinstance(response, str) else str(response)):
        fallback_raw = llm.invoke(f"Answer the following question using your general knowledge:\n{question}")
        fallback_answer = fallback_raw.content if hasattr(fallback_raw, "content") else str(fallback_raw)

        return f"(Note: This answer is based on general AI knowledge, not your uploaded document.)\n\n{fallback_answer}"

    return response

