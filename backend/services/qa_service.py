import os
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.chains.combine_documents import create_stuff_documents_chain
from services.llm import get_gemma_llm
from services.query_embedder import get_query_embedding
from langchain_core.embeddings import Embeddings  # for DummyEmbeddings

PERSIST_ROOT = "vector_store/"

# Dummy Embeddings object to satisfy FAISS load
class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        raise NotImplementedError("Not used in this context.")

    def embed_query(self, text):
        raise NotImplementedError("Not used in this context.")


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

    print("persist path",persist_path)

    if not os.path.exists(persist_path):
        raise ValueError(f"No vector index found for: {pdf_name}")

    vectordb = FAISS.load_local(
        persist_path,
        embeddings=DummyEmbeddings(),
        allow_dangerous_deserialization=True
    )

    query_embedding = get_query_embedding(question)

    docs = vectordb.max_marginal_relevance_search_by_vector(
        query_embedding,
        k=top_k,
        fetch_k=15,
        lambda_mult=0.8
    )

    if not docs:
        return "Sorry, no relevant content was found in this document."

    llm = get_gemma_llm()

    chain = create_stuff_documents_chain(
        llm=llm,
        prompt=QA_PROMPT,
        document_variable_name="input_documents"
    )

    response = chain.invoke({
        "input_documents": docs,
        "question": question
    })

    if is_not_in_doc(response if isinstance(response, str) else str(response)):
        fallback_raw = llm.invoke(f"Answer the following question using your general knowledge:\n{question}")
        fallback_answer = fallback_raw.content if hasattr(fallback_raw, "content") else str(fallback_raw)

        return f"(Note: This answer is based on general AI knowledge, not your uploaded document.)\n\n{fallback_answer}"

    return response
