import os
import json
from agent.utils.vectorstore_loader import load_vectorstore_from_path
from agent.utils.summarizer import batch_summarize_chunks

def summarize_file(state: dict) -> dict:
    file_path = state.get("parameters", {}).get("file_path")
    
    if not file_path:
        return {**state, "error": "Missing file_path"}

    full_path = os.path.join("vector_store", file_path)
    
    if not os.path.exists(full_path):
        return {**state, "error": f"Vector store not found at {full_path}"}

    try:
        vectorstore = load_vectorstore_from_path(full_path)
        chunks = [doc.page_content for doc in vectorstore.docstore._dict.values()]

        metadata_path = os.path.join(full_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            total_tokens = metadata.get("total_tokens", "unknown")
            num_chunks = metadata.get("num_chunks", len(chunks))
        else:
            total_tokens = "unknown"
            num_chunks = len(chunks)

        summary = batch_summarize_chunks(chunks)

        state["action"] = "summarize_file"
        state["summary"] = {
            "file": os.path.basename(file_path) + ".pdf",
            "summary": summary,
            "total_tokens": total_tokens,
            "num_chunks": num_chunks
        }
        return state

    except Exception as e:
        return {
            **state,
            "action": "summarize_file",
            "error": f"Error while summarizing file: {str(e)}"
        }
