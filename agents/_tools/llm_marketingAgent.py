# llm_chain.py
import os
from langchain import PromptTemplate, LLMChain #langchain_community.llms
from langchain_openai import AzureChatOpenAI  # Use the Azure-specific Chat model integration
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()
endpoint = os.getenv("ENDPOINT_URL")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")


llm = AzureChatOpenAI(
	azure_endpoint   = endpoint,   
	api_key          = SecretStr(subscription_key) if subscription_key else None,
	api_version      = version,
	azure_deployment = deployment, 
	temperature      = 0.3,
)
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

    # Create a chain that pairs the prompt with the Azure LLM.
    chain = LLMChain(llm=llm, prompt=template)
    return chain

def generate_marketing_strategy(input_text: str) -> str:
    chain = create_marketing_strategy_chain()
    response = chain.run(input_text=input_text)
    return response
