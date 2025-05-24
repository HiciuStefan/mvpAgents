import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import getpass
from langchain import hub
from langchain.agents import (
    create_react_agent,
    AgentExecutor,
)
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from tools import get_profile_url_tavily

load_dotenv()

if "AZURE_OPENAI_API_KEY" not in os.environ:
	os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
		"Enter your AzureOpenAI API key: "
	)
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://openai-vasi.openai.azure.com/openai/deployments/gpt-35-turbo-vasi/chat/completions?api-version=2025-01-01-preview"

# Inițializează modelul LLM
llm = AzureChatOpenAI(
    temperature=0,
    api_version="2025-01-01-preview",
    azure_deployment="gpt-35-turbo-vasi"
)



def generate_reply(tweet_text: str) -> str:
    """
    Generate a friendly short answer for a tweet.
    """
    prompt = f"""You are a helpful AI assistant that writes thoughtful, concise Twitter replies.
Tweet: "{tweet_text}"
Reply:"""
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error generating the answer: {e}")
        return "Thank you for sharing your thoughts!"
    


def lookup(name: str) -> str:
    llm = AzureChatOpenAI(
        temperature=0,
        api_version="2025-01-01-preview",
        azure_deployment="gpt-35-turbo-vasi"
    )

    template = """given the full name {name_of_person} I want you to get me a link to their Linkedin profile page.
                          Your answer should contain only a URL"""

    prompt_template = PromptTemplate(
        template=template, input_variables=["name_of_person"]
    )

    tools_for_agent = [
        Tool(
            name="crawl google for the linkedin profile page",
            func=get_profile_url_tavily,
            description="useful for when you need get the Linkedin Page URL",
        )
    ]

    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True, handle_parsing_errors=True)

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(name_of_person=name)}
    )

    linked_profile_url = result["output"]
    return linked_profile_url




if __name__=="__main__":
    print("Running...")
    print(generate_reply("Hellow Twitter World!"))
    print(lookup("Razvan Dumitrescu"))