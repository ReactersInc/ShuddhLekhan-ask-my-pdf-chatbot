from services.llm import get_gemini_flash_llm
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import os


def generate_summary(text):
    llm = get_gemini_flash_llm()
    docs = [Document(page_content=text)]
    chain = load_summarize_chain(llm, chain_type="stuff")
    summary = chain.run(docs)
    
    return summary

def save_summary(summary , filename):
    os.makedirs("summaries" , exist_ok=True)
    with open(f"summaries/{filename}.txt","w") as f:
        f.write(summary)