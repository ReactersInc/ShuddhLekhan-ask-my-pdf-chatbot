import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from google import generativeai as genai

load_dotenv()

def get_gemma_llm():
    # Load API key if not already in environment
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY is not set in the environment")
    
    # Initializing Gemma 3 now (Gemini 2.0) Flash model via LangChain
    llm = init_chat_model("gemma-3-27b-it", model_provider="google_genai")

    return llm


# --- Gemini 2.5 Flash Lite (via native SDK) ---
def get_gemini_flash_2_5_lite_llm():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY is not set in the environment")

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash-lite")
