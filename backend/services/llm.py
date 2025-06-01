from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",  
    openai_api_key="your-openai-key"  
)
