import os
from Doc_agent.utils.vectorstore_loader import get_all_vector_dirs_in_folder, load_vectorstore_from_path
from Doc_agent.utils.summarizer import batch_summarize_chunks

def file_topic_lookup(state: dict) -> dict:
    parameters = state.get("parameters", {})
    topic = parameters.get("topic")
    folder_path = parameters.get("folder_path", "").strip()

    if not topic:
        return {**state, "error": "Missing topic for lookup"}

    # Determine root to search from
    if folder_path:
        search_root = os.path.join("vector_store", folder_path)
    else:
        search_root = "vector_store"

    if not os.path.exists(search_root):
        return {**state, "error": f"Folder path '{search_root}' does not exist"}

    vector_dirs = get_all_vector_dirs_in_folder(search_root)
    results = []

    for vector_dir in vector_dirs:
        try:
            vectorstore = load_vectorstore_from_path(vector_dir)

            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 10}
            )
            relevant_docs = retriever.get_relevant_documents(topic)

            if not relevant_docs:
                continue

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
