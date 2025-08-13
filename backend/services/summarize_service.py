import os
from langchain_community.vectorstores import FAISS  # changed from Chroma
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.llm import get_gemma_llm

from transformers import AutoTokenizer

# Initializing tokenizer once
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))

PERSIST_ROOT = "vector_store"
VECTOR_STORE_TYPE = "faiss"  # change to "chroma" to switch

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
        Can you please summarize the following content concisely in a paragraph layout covering each topic and avoid repetition.
        Text:
        {text}
        Summary:
        """
)

def summarize_from_indexed_pdf(pdf_name, embedding_model, llm_model, query=None, top_k=3):
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    if VECTOR_STORE_TYPE == "faiss":
        vectordb = FAISS.load_local(persist_dir, embedding_model, allow_dangerous_deserialization=True)
    elif VECTOR_STORE_TYPE == "chroma":
        from langchain_chroma import Chroma
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    else:
        raise ValueError(f"Unsupported VECTOR_STORE_TYPE: {VECTOR_STORE_TYPE}")

    docs = vectordb.similarity_search(
        query or "",
        k=top_k,
        filter={"type": "text"}           
    )

    chain = LLMChain(llm=llm_model, prompt=SUMMARY_PROMPT)

    combined_text = "\n".join([doc.page_content for doc in docs])
    total_tokens = count_tokens(combined_text)
    
    summary = chain.run(text=combined_text)

    # Log to file
    with open("token_log.txt", "a") as f:
        f.write(f"{pdf_name}: {total_tokens} input tokens, {len(tokenizer.encode(summary))} output tokens\n")

    return summary


# This stays the same — no vector store used
def summarize_text(full_text: str, llm=None) -> str:
    if llm is None:
        llm = get_gemma_llm()
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks   = splitter.split_text(full_text)

    prompt   = PromptTemplate(
        input_variables=["text"],
        template="""
Can you please summarize the following content concisely in a paragraph layout covering each topic and avoid repetition.
{text}
"""
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(text="\n\n".join(chunks))