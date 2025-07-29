from langgraph.graph import StateGraph, END
from agent.nodes.router import route_query
from agent.nodes.folder_summarizer import summarize_folder
from agent.nodes.file_summarizer import summarize_file
from agent.nodes.file_topic_lookup import file_topic_lookup
from agent.nodes.path_resolver import resolve_file_path, resolve_folder_path

# Define input/output schema (shared state)
State = dict

# Create the LangGraph
graph = StateGraph(State)

# Add all nodes
graph.add_node("router", route_query)
graph.add_node("summarize_folder", summarize_folder)
graph.add_node("summarize_file", summarize_file)
graph.add_node("file_topic_lookup", file_topic_lookup)
graph.add_node("resolve_file_path", resolve_file_path)
graph.add_node("resolve_folder_path", resolve_folder_path)

# Router decides the next node
graph.set_entry_point("router")

# Routing logic based on state's "action" key
def router_next_node(state):
    action = state.get("action", "")
    params = state.get("parameters", {})

    # Summarize File: resolve file_path if only file_name is given
    if action == "summarize_file" and not params.get("file_path"):
        return "resolve_file_path"

    # Summarize Folder: resolve folder_path if only folder_name is given
    elif action == "summarize_folder" and not params.get("folder_path"):
        return "resolve_folder_path"

    elif action == "file_topic_lookup" and not params.get("folder_path"):
        state["parameters"]["folder_path"] = ""  # empty = Scanning all directories
        return "file_topic_lookup"

    return action


graph.add_conditional_edges("router", router_next_node)

# Route resolution steps
graph.add_edge("resolve_file_path", "summarize_file")
graph.add_edge("resolve_folder_path", "summarize_folder")

# Terminal nodes: each task ends after one run
graph.add_edge("summarize_folder", END)
graph.add_edge("summarize_file", END)
graph.add_edge("file_topic_lookup", END)

# Compile the graph
agent_executor = graph.compile()
