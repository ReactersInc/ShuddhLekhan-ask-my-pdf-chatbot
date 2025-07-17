import os
from langchain_chroma import Chroma
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

def summarize_from_indexed_pdf(pdf_name, embedding_model, llm_model, query=None, top_k=3):
    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)

    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding_model) 

    docs = vectordb.similarity_search(
        query or "",
        k=top_k,
        filter={"type": "text"}           
    )

    chain = LLMChain(llm=llm_model, prompt=SUMMARY_PROMPT)  

    combined_text = "\n".join([doc.page_content for doc in docs])
    summary = chain.run(text=combined_text)

    return summary

#  just sending the text to backend
def summarize_text(full_text: str, llm=None) -> str:
    if llm is None:
        llm = get_gemini_flash_llm()
        
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