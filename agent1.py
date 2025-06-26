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
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://alex-test-1112.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview"

# Inițializează modelul LLM
llm = AzureChatOpenAI(
    temperature=0,
    api_version="2025-01-01-preview",
    azure_deployment="2025-01-01-preview"
)

def lookup(name: str) -> str:

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
    print(lookup("Razvan Dumitrescu"))