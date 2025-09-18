import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, SecretStr, ValidationError
import json
from supabase import create_client, Client
from typing import Dict, List, Any

PROMPT_TABLE= "Prompt"
PROMPT_NAME = "prompt_name"
PROMPT_PAYLOAD = "prompt_payload"
SYSTEM_USER_CONTEXT_PROMP = "system_user_context_prompt"
CONTENT = "content"

class LLMRespSchema(BaseModel):
	short_description: str
	actionable: bool  
	suggested_action: str 
	relevance: str  
	suggested_reply: str 

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_API_BASE")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url is None or supabase_key is None:
	raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

supabase: Client = create_client(supabase_url, supabase_key)

FALLBACK_RESPONSE = LLMRespSchema(
			# category="Unknown",
			short_description="",
			actionable=False,
			suggested_action="",
			relevance="",
			suggested_reply=""
		)

llm = AzureChatOpenAI(
	azure_endpoint   = endpoint,   
	api_key          = SecretStr(subscription_key) if subscription_key else None,
	api_version      = version,
	azure_deployment = deployment, 
	temperature      = 1,
)

def get_supabase_prompt(prompt: str, email_text: str, db_history_text: str):
    """
    Loads JSON content from a specific item in the 'items' table in Supabase.
    """
    try:
        res = supabase.table(PROMPT_TABLE).select(PROMPT_PAYLOAD).eq(PROMPT_NAME, prompt).single().execute()
        if res.data and PROMPT_PAYLOAD in res.data:
            return res.data[PROMPT_PAYLOAD]
        else:
            print(f"No data or {PROMPT_PAYLOAD} found for item: {prompt}")
            return None
    except Exception as e:
        print(f"Error loading {prompt} from Supabase: {e}")
        return None
	
def get_enhanced_prompt(prompt:  List[Dict[str, Any]], email_text: str, db_history_text: str):

	prompt[1][CONTENT] += db_history_text
	prompt[2][CONTENT] += email_text
	return prompt

def get_email_enhancements(email_text: str, db_history_text: str) -> LLMRespSchema:
	try:
		# Load prompt from Supabase
		supabase_prompt = get_supabase_prompt(SYSTEM_USER_CONTEXT_PROMP,email_text,db_history_text)
		email_and_history_prompt=get_enhanced_prompt(supabase_prompt,email_text,db_history_text) if supabase_prompt else None
		
		if email_and_history_prompt is None:
			return FALLBACK_RESPONSE
		else:	
			messages = email_and_history_prompt

		ai_msg = llm.invoke(messages)
		raw = ai_msg.content
		
		# coalesce list→str if necessary:
		if isinstance(raw, list):
			raw = "".join(str(item) for item in raw)

		try:
			data = json.loads(raw)  # your parsed JSON
			email_enhancements: LLMRespSchema = LLMRespSchema(**data)
			return email_enhancements
		
		except json.JSONDecodeError as e:
			# TODO remove print, use logging
			# print(f"❌ JSON parsing failed: {e}")

			logger = logging.getLogger(__name__)
			logger.error("JSON decoding failed", exc_info=e)

			# Return a fallback LLMRespSchema instance on JSON error
			return FALLBACK_RESPONSE
		
		except ValidationError as exc:

			logger = logging.getLogger(__name__)
			logger.error("Validation failed", exc_info=exc)

			# this will include missing-fields, wrong-types, extra-fields
			raise RuntimeError(f"Invalid response schema from LLM:\n{exc}")

	except Exception as e:
		# TODO remove print, use logging
		# print(f"Error processing email text: {e}")
			
		logger = logging.getLogger(__name__)
		logger.error("Other exception", exc_info=e)
		
		# Return a fallback LLMRespSchema instance
		return FALLBACK_RESPONSE


