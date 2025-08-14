from services.llm import get_gemini_flash_2_5_lite_llm
from pathlib import Path

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "summarizer_prompt.txt"

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

SUMMARIZER_PROMPT = load_prompt()

def batch_summarize_chunks(docs, chunk_token_limit=250000):
    """
    docs: list of Document objects with .metadata['tokens']
    """
    llm = get_gemini_flash_2_5_lite_llm()
    summaries = []

    batch_chunks = []
    batch_tokens = 0

    for doc in docs:
        tokens = doc.metadata.get("tokens", len(doc.page_content.split()))
        
        if batch_tokens + tokens > chunk_token_limit:
            # Summarize current batch
            batch_text = "\n\n".join(d.page_content for d in batch_chunks)
            prompt = SUMMARIZER_PROMPT.replace("{{content}}", batch_text.strip())
            response = llm.invoke(prompt)
            summary = response.content.strip()  # FIX: Use `.content`
            summaries.append(summary)

            # Start new batch
            batch_chunks = [doc]
            batch_tokens = tokens
        else:
            batch_chunks.append(doc)
            batch_tokens += tokens

    # Final batch
    if batch_chunks:
        batch_text = "\n\n".join(d.page_content for d in batch_chunks)
        prompt = SUMMARIZER_PROMPT.replace("{{content}}", batch_text.strip())
        response = llm.invoke(prompt)
        summary = response.content.strip()  # FIX: Use `.content`
        summaries.append(summary)

    return "\n".join(summaries)
