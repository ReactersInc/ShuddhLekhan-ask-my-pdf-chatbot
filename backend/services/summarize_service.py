import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from services.llm import get_gemini_flash_llm

PERSIST_ROOT = "vector_store"

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
        Can you please summarize the following content concisely in a paragraph layout covering each topic and avoid repetition.
        Text:
        {text}
        Summary:
        """
)

def summarize_from_indexed_pdf(pdf_name, query=None, top_k=3):
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    docs = vectordb.similarity_search(query or "", k=top_k)

    llm = get_gemini_flash_llm()

    chain = LLMChain(llm=llm, prompt=SUMMARY_PROMPT)

    combined_text = "\n".join([doc.page_content for doc in docs])
    summary = chain.run(text=combined_text)

    return summary
