import os
from agent.utils.vectorstore_loader import get_all_vector_dirs_in_folder, load_vectorstore_from_path
from agent.utils.summarizer import batch_summarize_chunks

def file_topic_lookup(state: dict) -> dict:
    topic = state.get("parameters", {}).get("topic")
    folder_path = state.get("parameters", {}).get("folder_path")

    if not topic or not folder_path:
        return {**state, "error": "Missing topic or folder_path"}

    vector_dirs = get_all_vector_dirs_in_folder(folder_path)
    results = []

    for vector_dir in vector_dirs:
        try:
            vectorstore = load_vectorstore_from_path(vector_dir)

            retriever = vectorstore.as_retriever(
                search_type="similarity",  # we can later switch to "mmr" or add thresholds
                search_kwargs={"k": 10}
            )
            relevant_docs = retriever.get_relevant_documents(topic)

            if not relevant_docs:
                continue  # skips this file if no relevant chunks

            chunks = [doc.page_content for doc in relevant_docs]
            summary = batch_summarize_chunks(chunks)

            results.append({
                "file": os.path.basename(vector_dir) + ".pdf",
                "summary": summary,
                "num_relevant_chunks": len(relevant_docs)
            })

        except Exception as e:
            results.append({
                "file": os.path.basename(vector_dir) + ".pdf",
                "summary": f"Error while retrieving: {str(e)}",
                "num_relevant_chunks": 0
            })

    if not results:
        state["message"] = "No relevant files found for this topic."

    state["action"] = "file_topic_lookup"
    state["results"] = results
    return state
