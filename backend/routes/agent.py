# routes/agent.py
# ----------------
# This file defines the API routes that connect the **frontend** (React app) 
# to the **LangGraph Agent** running in the backend.
#
# The main purpose of this route is to receive a natural language query 
# from the frontend (e.g., "summarize folder Reports"), forward it to the 
# LangGraph agent executor, and return the AI-generated response back to 
# the frontend in JSON format.
#


from flask import Blueprint, request, jsonify
from Doc_agent.langgraph_agent import agent_executor

# Create a Blueprint so this route can be registered in app.py
agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/query", methods=["POST"])
def agent_query():
    """
    API endpoint for AI document queries.
    
    Expects JSON body: {"query": "some question"}
    
    Example request:
      POST /agent/query
      {
        "query": "summarize folder Reports"
      }

    Returns:
      - JSON response containing agent output
      - If error, returns {"error": "..."}
    """
    try:
        # Get the query from frontend
        data = request.get_json()
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Step 1: prepare initial state for LangGraph agent
        initial_state = {
            "query": query,
            "conversation_state": {}  # can be extended later for memory
        }

        # Step 2: invoke LangGraph agent with the query
        final_state = agent_executor.invoke(initial_state)

        # Step 3: return the AI agent's output back to frontend
        return jsonify(final_state)

    except Exception as e:
        # Catch unexpected errors (e.g., agent crash, JSON issues)
        return jsonify({"error": str(e)}), 500
