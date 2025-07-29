import json 
from services.llm import get_gemini_flash_llm
from pathlib import Path

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "router_prompt.txt"

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
ROUTER_PROMPT = load_prompt()

def route_query(state:dict)->dict:
    query = state.get("query" , "")
    conversation_state = state.get("conversation_state", {})

    llm = get_gemini_flash_llm()

    #Build Prompt with conversation state and user query
    prompt = ROUTER_PROMPT + "\n\n"
    prompt += f"Conversation state: {json.dumps(conversation_state)}\n"
    prompt += f"User query: {query}\n"

    result_raw = None
    result = None
    
    try:
        result_raw = llm.invoke(prompt)
        result = result_raw.content.strip()

        # Remove markdown formatting if present
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()

        action_data = json.loads(result)

    except Exception as e:
        print("\n❌ ROUTER ERROR")
        print("Prompt sent to LLM:\n", prompt)
        print("LLM raw result:\n", result_raw)
        print("Cleaned result:\n", result)
        print("Exception:\n", str(e))
        print("-----------------\n")
        return {**state, "error": str(e)}

    


    
    # Update state with router decision
    state.update({
        "action": action_data.get("action", ""),
        "parameters": action_data.get("parameters", {}),
        "router_message": action_data.get("message", "")
    })

    return state