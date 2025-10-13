from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
import os
from dotenv import load_dotenv
import json

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_API_BASE")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")
RAG_URL_GET=""


llm = AzureChatOpenAI(
	azure_endpoint   = endpoint,   
	api_key          = SecretStr(subscription_key) if subscription_key else None,
	api_version      = version,
	azure_deployment = deployment, 
	temperature      = 0.3,
)

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
        # retrieved_context = get_relevant_context_from_rag(scenario_name, NEW_EMAIL if NEW_EMAIL is not None else "email")  # Your RAG function
        # print (f"✅ Retrieved context: {retrieved_context}")
        # Step 3: Create the user prompt
        # user_prompt = f'''RELEVANT CONTEXT from previous emails:
        # {retrieved_context}

        # NEW EMAIL to analyze:
        # {new_email_text}

        # Analyze the new email using the historical context. Focus on identifying patterns, connections, and any missing information that was important in similar previous situations.'''

        # Step 4: Create messages array for your LLM
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                # "content": user_prompt
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
     run_scenario("context/pozitive_scenario_1",  "")
    # delete_payload(emails)
    # if not emails:
    #     print("ℹ️ No emails returned by workflow.")
    # else:
    #     for email in emails:
    #         send_email_payload(email)

except Exception as main_err:
    print(f"🚨 Failed to run workflow: {main_err}")
