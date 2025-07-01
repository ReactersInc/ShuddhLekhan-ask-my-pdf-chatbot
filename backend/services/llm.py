import os
from langchain.chat_models import init_chat_model

def get_gemini_flash_llm():
    # Load API key if not already in environment
    
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY is not set in the environment")
    
    # Initializing Gemma 3 now (Gemini 2.0) Flash model via LangChain
    llm = init_chat_model("gemma-3-27b-it", model_provider="google_genai")
    return llm