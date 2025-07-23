from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import json

# from agents._tools.llm_emailAgent import return_email_label

load_dotenv()
RAG_URL_POST_DELETE =  os.getenv("RAG_URL_POST_DELETE")  
RAG_URL_GET =  os.getenv("RAG_URL_GET") 
EMAIL_AGENT_API_KEY = os.getenv("EMAIL_AGENT_API_KEY")

NEW_EMAIL = os.getenv("NEW_EMAIL")
NEW_TWITTER = os.getenv("NEW_TWITTER")
NEW_WEBSITE = os.getenv("NEW_WEBSITE")

headers = {
    "Content-Type": "application/json",
    "X-API-key": EMAIL_AGENT_API_KEY
}

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_API_BASE")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")


llm = AzureChatOpenAI(
	azure_endpoint   = endpoint,   
	api_key          = SecretStr(subscription_key) if subscription_key else None,
	api_version      = version,
	azure_deployment = deployment, 
	temperature      = 0.3,
)

def insert_base_context(context_file: str):
    """Read a JSON file and insert each context object into the database."""
    try:
        if RAG_URL_POST_DELETE is None:
                    raise ValueError("RAG_URL_POST_DELETE environment variable is not set.")
        
        with open(context_file, 'r') as file:
            data = json.load(file)
            context_list = data.get("context", [])

            for item in context_list:   
                # Insert into RAG
                payload = {
                    "input": item.get("body", "")
                }
                response = requests.post(RAG_URL_POST_DELETE, json=payload, headers=headers, timeout=10)
                response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
                print(f"✅ Sent {item.get("subject", "")},Response: {response.status_code}")

    except FileNotFoundError:
        print(f"⚠️ Context file '{context_file}' not found.")
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse JSON in '{context_file}'.")
    except Exception as err:
        print(f"⚠️ Unexpected error during delete: {err}")

def delete_base_context():
    try:
        if RAG_URL_POST_DELETE is None:
            raise ValueError("RAG_URL_POST_DELETE environment variable is not set.")
        confirmation ={
                        "confirm" : True
                }
        response = requests.delete(RAG_URL_POST_DELETE, json=confirmation, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        print(f"✅ Rag deletion response: {response.status_code}")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error during delete: {http_err}")
    except requests.exceptions.Timeout:
        print(f"⌛ Timeout during delete")
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection error during delete")
    except Exception as err:
        print(f"⚠️ Unexpected error during delete: {err}")
        
def get_relevant_context_from_rag(scenario_name: str,type: str)->str:
    """Run a specific scenario by sending a POST request to the RAG URL."""
    try:
        if RAG_URL_GET is None:
            raise ValueError("RAG_URL_GET environment variable is not set.")
        
        with open(scenario_name, 'r') as file:
            data = json.load(file)
            scenario=data.get(type, {})
            payload = {
                    "text": scenario.get("body", "")
                }
        response = requests.get(RAG_URL_GET, params=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        response_data = response.json()
        documents = response_data.get("data", {}).get("documents", [])

        for i, doc in enumerate(documents, start=1):
            content = doc.get("content", "")
            print(f"{i}. {content}")

        context_list = [doc.get("content", "") for doc in documents]
        return "\n".join(context_list)
        print(f"✅ Scenario '{scenario_name}' executed successfully. Response: {response.status_code}")

        # return_email_label(scenario,response.text)
        return json.dumps(response.json())
    
    except FileNotFoundError:
        return f"⚠️ Scenario file '{scenario_name}' not found."
    except json.JSONDecodeError:
        return f"⚠️ Failed to parse JSON in '{scenario_name}'."
    except requests.exceptions.HTTPError as http_err:
        return f"❌ HTTP error during scenario execution: {http_err}"
    except requests.exceptions.Timeout:
        return "⌛ Timeout during scenario execution"
    except requests.exceptions.ConnectionError:
        return "🚫 Connection error during scenario execution"
    except Exception as err:
        return f"⚠️ Unexpected error during scenario execution: {err}"
    
def run_scenario(scenario_name: str,type: str):

    try:
        if RAG_URL_GET is None:
            raise ValueError("RAG_URL_GET environment variable is not set.")
        
        with open(scenario_name, 'r') as file:
            data = json.load(file)
            scenario=data.get(type, {})
            new_email_text = scenario.get("body", "")
        if not new_email_text:
            return "ℹ️ No new email text provided for analysis."
        # Step 1: Extract the system prompt
        system_prompt = '''You are an intelligent business AI assistant specializing in email analysis and strategic recommendations. Your primary function is to analyze business emails using historical context to identify patterns, connections, and actionable opportunities.

        CORE CAPABILITIES:
        • Pattern Recognition: Identify recurring themes, requirements, and business relationships from historical context
        • Contextual Analysis: Connect new emails to relevant past communications to uncover missing information or implied requirements
        • Strategic Recommendations: Provide actionable suggestions based on historical patterns and business context

        ANALYSIS FRAMEWORK:
        1. Examine the new email for key business elements (requests, opportunities, stakeholders, requirements)
        2. Identify connections and patterns between the new email and historical context
        3. Note any missing information that was important in previous similar situations
        4. Determine if the email requires action based on business impact

        ACTIONABLE CRITERIA:
        An email is actionable if it pertains to:
        • Business opportunities or potential partnerships
        • Product announcements or service requests
        • Customer engagement or relationship management
        • Market signals or competitive intelligence
        • Collaboration requests or project coordination
        • Issues requiring follow-up or clarification

        RECOMMENDATION QUALITY:
        • Suggested actions must be based on logical reasoning derived from context analysis
        • Relevance explanations should clearly connect historical patterns to current situation
        • Focus on what actions would prevent missed opportunities or resolve potential issues

        OUTPUT FORMAT:
        Return analysis in JSON format with:
        • analysis: Your reasoning process and pattern identification
        • short_description: Concise summary (max 60 chars)
        • actionable: Boolean indicating if action is needed
        • suggested_action: Specific recommended action (max 40 chars) - only if actionable
        • relevance: Why this action matters based on context (max 100 chars) - only if actionable

        If not actionable, set suggested_action and relevance to empty strings ("").'''

        # Step 2: Your RAG retrieval (you already have this)
        retrieved_context = get_relevant_context_from_rag(scenario_name, NEW_EMAIL if NEW_EMAIL is not None else "email")  # Your RAG function
        print (f"✅ Retrieved context: {retrieved_context}")
        # Step 3: Create the user prompt
        user_prompt = f'''RELEVANT CONTEXT from previous emails:
        {retrieved_context}

        NEW EMAIL to analyze:
        {new_email_text}

        Analyze the new email using the historical context. Focus on identifying patterns, connections, and any missing information that was important in similar previous situations.'''

        # Step 4: Create messages array for your LLM
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        # Step 5: Call your LLM
        ai_response = llm.invoke(messages)

        # Step 6: Parse JSON response

        if isinstance(ai_response.content, str):
            raw = ai_response.content.strip()

            if raw.startswith("```json") and raw.endswith("```"):
                # Remove the wrapping lines
                lines = raw.splitlines()
                json_str = "\n".join(lines[1:-1])
            else:
                json_str = raw
            result = json.loads(json_str)
            print(f"✅ JSON parsed successfully: {result}")
            
        else:
            result = ai_response.content
            print(f"✅ LLM response is not a string, using as is: {result}")

        
    except FileNotFoundError:
        return f"⚠️ Scenario file '{scenario_name}' not found."
    except Exception as err:
        return f"⚠️ Unexpected error during scenario execution: {err}"


# Run the workflow
try:
    # result = workflow.invoke({})
    # emails = result.get("emails", [])
    #get_payload_for_client("Anca Irom")
    # insert_base_context("context/base_context.json")
    run_scenario("context/pozitive_scenario_1", NEW_EMAIL if NEW_EMAIL is not None else "")
    # delete_payload(emails)
    # if not emails:
    #     print("ℹ️ No emails returned by workflow.")
    # else:
    #     for email in emails:
    #         send_email_payload(email)

except Exception as main_err:
    print(f"🚨 Failed to run workflow: {main_err}")



        # messages=[
        #             {
        #             "system_prompt": {
        #                 "role": "system",
        #                 "content": "You are an intelligent business AI assistant specializing in email analysis "
        #                 "and strategic recommendations. Your primary function is to analyze business emails using "
        #                 "historical context to identify patterns, connections, and actionable opportunities."
        #                 "\n\nCORE CAPABILITIES:\n• Pattern Recognition: Identify recurring themes, requirements, "
        #                 "and business relationships from historical context\n• Contextual Analysis: "
        #                 "Connect new emails to relevant past communications to uncover missing information or "
        #                 "implied requirements\n• Strategic Recommendations: Provide actionable suggestions based "
        #                 "on historical patterns and business context\n\nANALYSIS FRAMEWORK:\n1. Examine the new "
        #                 "email for key business elements (requests, opportunities, stakeholders, requirements)\n2. "
        #                 "Identify connections and patterns between the new email and historical context\n3. "
        #                 "Note any missing information that was important in previous similar situations\n4. "
        #                 "Determine if the email requires action based on business impact\n\nACTIONABLE CRITERIA:\n"
        #                 "An email is actionable if it pertains to:\n• Business opportunities or potential "
        #                 "partnerships\n• Product announcements or service requests\n• Customer engagement or "
        #                 "relationship management\n• Market signals or competitive intelligence\n• Collaboration "
        #                 "requests or project coordination\n• Issues requiring follow-up or clarification\n\n"
        #                 "RECOMMENDATION QUALITY:\n• Suggested actions must be based on logical reasoning derived "
        #                 "from context analysis\n• Relevance explanations should clearly connect historical patterns "
        #                 "to current situation\n• Focus on what actions would prevent missed opportunities or resolve "
        #                 "potential issues\n\nOUTPUT FORMAT:\nReturn analysis in JSON format with:\n• analysis: "
        #                 "Your reasoning process and pattern identification\n• short_description: Concise summary "
        #                 "(max 60 chars)\n• actionable: Boolean indicating if action is needed\n• suggested_action: "
        #                 "Specific recommended action (max 40 chars) - only if actionable\n• relevance: Why this action "
        #                 "matters based on context (max 100 chars) - only if actionable\n\nIf not actionable, set "
        #                 "suggested_action and relevance to empty strings (\"\")."
        #             },
        #             "user_context_prompt": "RELEVANT CONTEXT from previous emails:\n{retrieved_context}\n\n"
        #             "NEW EMAIL to analyze:\n{new_email}\n\nAnalyze the new email using the historical context. "
        #             "Focus on identifying patterns, connections, and any missing information that was important "
        #             "in similar previous situations.",
                    
        #             "example_usage": {
        #                 "retrieved_context": "Following our discussions, we need a Senior AI Developer for our international expansion team. IMPORTANT: Must be able to travel internationally at least 2 times per month as part of our distributed international team. Budget: $85-95K annually.\n\nGreat news! After interviews, we're extending an offer to Alex Rodriguez. He impressed us with his enthusiasm for the international travel aspect. Travel budget: $15,000 annually for international trips.",
                        
        #                 "new_email": "Hope you're well! Alex has been performing excellently and has integrated well with our international team. Due to rapid expansion success, we need another AI Developer to join our international team. The role is similar to Alex's position: Mid-level AI Developer, computer vision focus, budget: $75-85K annually. Can you help us find another strong candidate?",
                        
        #                 "expected_output": {
        #                 "analysis": "Client requests another developer for their 'international team' - same team Alex joined. Historical pattern shows international team roles specifically required 2x monthly travel and had dedicated travel budgets. Client mentions role is 'similar to Alex's position' but omits travel requirements that were critical in previous placement.",
        #                 "short_description": "Request for AI developer for international team",
        #                 "actionable": True,
        #                 "suggested_action": "Clarify travel requirements",
        #                 "relevance": "Previous international roles required 2x monthly travel - need to confirm same applies"
        #                 }
        #             },
                    
        #             "implementation_code": 
        #             "messages = [\n    "
        #             "{\n        'role': 'system',"
        #             "\n        'content': system_prompt\n    },"
        #             "\n    {\n        'role': 'user',"
        #             " \n        'content': f'RELEVANT CONTEXT from previous emails:\\n{retrieved_context}"
        #             "\\n\\nNEW EMAIL to analyze:\\n{new_email}\\n\\nAnalyze the new email using the historical "
        #             "context. Focus on identifying patterns, connections, and any missing information that was "
        #             "important in similar previous situations.'\n    }\n]\n\n"
        #             "ai_response = llm.invoke(messages)"
        #             }
        #         ]