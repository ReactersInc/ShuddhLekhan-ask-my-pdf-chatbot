from services.llm import get_gemini_flash_llm
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import os

def generate_summary(text):
    llm = get_gemini_flash_llm()
    docs = [Document(page_content=text)]
    chain = load_summarize_chain(llm, chain_type="stuff")
    result = chain.invoke({"input_documents": docs})
    print("DEBUG - chain.invoke result:", result)
    
    # Make sure to extract only the summary text string
    if isinstance(result, dict) and "text" in result:
        return result["text"]
    else:
        # If it's already a string or unexpected, just convert to str
        return str(result)


def save_summary(summary, filename):
    os.makedirs("summaries", exist_ok=True)
    with open(f"summaries/{filename}.txt", "w") as f:
        # If summary is dict with a 'text' key:
        if isinstance(summary, dict) and 'text' in summary:
            f.write(summary['text'])
        else:
            f.write(str(summary))  # fallback to convert to string
