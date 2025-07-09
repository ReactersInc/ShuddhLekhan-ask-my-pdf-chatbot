import json
from agent.langgraph_agent import agent_executor

def run_cli():
    print("\n Agentic PDF Assistant (LangGraph CLI)")
    print("Type 'exit' to quit.\n")

    conversation_state = {}  # can be extended in future

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            # Step 1: prepare initial state
            initial_state = {
                "query": user_query,
                "conversation_state": conversation_state
            }

            # Step 2: invoke LangGraph agent
            final_state = agent_executor.invoke(initial_state)

            # Step 3: print results
            print("\nAssistant:")
            if "error" in final_state:
                print("⚠️ Error:", final_state["error"])
            elif final_state.get("action") == "summarize_folder":
                for summary in final_state.get("summaries", []):
                    print(f"\n File: {summary['file']}")
                    print(f" Summary:\n{summary['summary']}")
            elif final_state.get("action") == "summarize_file":
                summary = final_state.get("summary", {})
                print(f"\n File: {summary.get('file')}")
                print(f" Summary:\n{summary.get('summary')}")
            elif final_state.get("action") == "file_topic_lookup":
                for result in final_state.get("results", []):
                    print(f"\n Relevant File: {result['file']} ({result.get('num_relevant_chunks', '?')} chunks)")
                    print(f" Summary:\n{result['summary']}")
            elif final_state.get("action") == "done":
                print("✅ Task completed.")
            else:
                print("🤖 Unknown action. Response:\n", json.dumps(final_state, indent=2))

        except Exception as e:
            print("⚠️ Exception:", str(e))

if __name__ == "__main__":
    run_cli()
