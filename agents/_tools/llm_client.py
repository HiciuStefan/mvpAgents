# llm_client.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION", "2025-01-01-preview"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini"),
    temperature=float(os.getenv("AZURE_TEMPERATURE", 0.3)),
)
