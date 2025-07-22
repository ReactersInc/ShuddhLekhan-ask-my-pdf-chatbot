from langgraph.graph import StateGraph, END
from agent.nodes.router import route_query
from agent.nodes.folder_summarizer import summarize_folder
from agent.nodes.file_summarizer import summarize_file
from agent.nodes.file_topic_lookup import file_topic_lookup

# Define input/output schema (shared state)
State = dict

# Create the LangGraph
graph = StateGraph(State)

# Add all nodes
graph.add_node("router", route_query)
graph.add_node("summarize_folder", summarize_folder)
graph.add_node("summarize_file", summarize_file)
graph.add_node("file_topic_lookup", file_topic_lookup)

# Router decides the next node
graph.set_entry_point("router")

# Routing logic based on state's "action" key
graph.add_conditional_edges(
    "router",
    # This function inspects the state and returns the name of the next node
    lambda state: state.get("action")
)

# Terminal nodes: each task ends after one run
graph.add_edge("summarize_folder", END)
graph.add_edge("summarize_file", END)
graph.add_edge("file_topic_lookup", END)

# Compile the graph
agent_executor = graph.compile()
