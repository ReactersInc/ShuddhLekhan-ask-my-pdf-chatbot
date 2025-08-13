import os
import json
from Doc_agent.utils.vectorstore_loader import load_vectorstore_from_path, get_all_vector_dirs_in_folder
from Doc_agent.utils.summarizer import batch_summarize_chunks

def summarize_folder(state: dict) -> dict:
    folder_path = state.get("parameters", {}).get("folder_path")
    if not folder_path:
        return {**state, "error": "Missing folder_path"}

    vector_dirs = get_all_vector_dirs_in_folder(folder_path)
    summaries = []

    for vector_dir in vector_dirs:
        try:
            vectorstore = load_vectorstore_from_path(vector_dir)

            # Use retriever with MMR strategy
            retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={
                "k": 5,         # number of final docs
                "fetch_k": 40,   # number of candidates to fetch before diversity filter
                "lambda_mult": 0.5  # Balance between diversity and relevance
            })

            query = "Summarize this document"
            docs = retriever.invoke(query)

            metadata_path = os.path.join(vector_dir, "metadata.json")

            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                total_tokens = metadata.get("total_tokens", "unknown")
                num_chunks = metadata.get("num_chunks", len(docs))
            else:
                total_tokens = "unknown"
                num_chunks = len(docs)

            summary = batch_summarize_chunks(docs)

            file_name = os.path.basename(vector_dir)
            summaries.append({
                "file": file_name + ".pdf",
                "summary": summary,
                "total_tokens": total_tokens,
                "num_chunks": num_chunks
            })

        except Exception as e:
            summaries.append({
                "file": os.path.basename(vector_dir) + ".pdf",
                "summary": f"Error during summarization: {str(e)}",
                "total_tokens": "unknown",
                "num_chunks": 0
            })

    state["action"] = "summarize_folder"
    state["summaries"] = summaries
    return state
