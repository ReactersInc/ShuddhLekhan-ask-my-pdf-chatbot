import os
from langchain.chat_models import init_chat_model

# Ensure GOOGLE_API_KEY is set
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError("Please set the GOOGLE_API_KEY environment variable.")

# Initialize Gemini 2.0 Flash
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
