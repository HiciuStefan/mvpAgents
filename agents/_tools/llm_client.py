# llm_client.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    # temperature=float(os.getenv("AZURE_TEMPERATURE", 0.3)),
)
