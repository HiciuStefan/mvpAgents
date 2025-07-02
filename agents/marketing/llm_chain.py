# llm_chain.py
import os
from langchain import PromptTemplate, LLMChain #langchain_community.llms
from langchain_openai import AzureChatOpenAI  # Use the Azure-specific Chat model integration

# Ensure your environment variables are correctly set.
# You can also set these in your OS or in a .env file if you prefer.
if "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = "ACYhswv9bdG9HLSwegzWBaepqA7mKYn3mQtHqU3hiTJzzbRO9qyOJQQJ99BEACfhMk5XJ3w3AAABACOGp1TG"
if "AZURE_OPENAI_API_BASE" not in os.environ:
    os.environ["AZURE_OPENAI_API_BASE"] = "https://openai-vasi.openai.azure.com/openai/deployments/gpt-35-turbo-vasi/chat/completions?api-version=2025-01-01-preview"

def create_marketing_strategy_chain():
    # Define the prompt template for generating the marketing strategy.
    prompt_template = """
    You are a marketing guru. Based on the following marketing input details, generate a detailed marketing campaign strategy.
    Include suggestions for campaign duration and post ideas for various platforms (e.g., social media, blogs).
    
    Marketing Input:
    {input_text}
    
    Strategy:
    """
    template = PromptTemplate(
        input_variables=["input_text"],
        template=prompt_template
    )
    
    # Initialize the LLM using AzureChatOpenAI.
    # Note: The azure_deployment parameter should match the deployment name in your Azure resource.
    llm = AzureChatOpenAI(
        azure_deployment="gpt-35-turbo-vasi",  # Replace with your actual deployment name
        api_version="2025-01-01-preview",        # Replace with your actual API version if needed
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        azure_endpoint=os.environ.get("AZURE_OPENAI_API_BASE"),
    )
    
    # Create a chain that pairs the prompt with the Azure LLM.
    chain = LLMChain(llm=llm, prompt=template)
    return chain

def generate_marketing_strategy(input_text: str) -> str:
    chain = create_marketing_strategy_chain()
    response = chain.run(input_text=input_text)
    return response
