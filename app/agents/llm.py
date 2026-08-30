import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Ensure the API key is available
groq_api_key = os.getenv("GROQ_API_KEY")

# The Director is a simpler/faster model
director_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    api_key=groq_api_key
)

# The Reviewer is also simpler
reviewer_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.1,
    api_key=groq_api_key
)

# The ScriptWriter is the complex model for structured output and tool use
scriptwriter_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.4,
    api_key=groq_api_key
)
