import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, SecretStr, ValidationError
import json
from supabase import create_client, Client
from ..email.rag import get_relevant_context_from_rag

PROMPT_TABLE= "Prompt"
NAME = "name"
VALUE = "value"
SYSTEM_PROMPT = "system_prompt"
USER_CONTEXT = "user_context"
JSON_INSTRUCTIONS = "json_instructions"

class AnalysisContent(BaseModel):
    short_description: str
    actionable: bool 
    suggested_action: str 
    relevance: str 
    suggested_reply: str
    priority_level: str
    opportunity_type: str

class LLMRespSchema(BaseModel):
    analysis: AnalysisContent

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_API_BASE")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")

NEW_EMAIL = os.getenv("NEW_EMAIL")
NEW_TWITTER = os.getenv("NEW_TWITTER")
NEW_WEBSITE = os.getenv("NEW_WEBSITE")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url is None or supabase_key is None:
	raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

supabase: Client = create_client(supabase_url, supabase_key)

FALLBACK_RESPONSE = LLMRespSchema(
analysis=AnalysisContent(
			short_description="",	
			actionable=False,		
			suggested_action="",
			relevance="",
			suggested_reply="",
			priority_level="",
			opportunity_type=""
		)
)

llm = AzureChatOpenAI(
	azure_endpoint   = endpoint,   
	api_key          = SecretStr(subscription_key) if subscription_key else None,
	api_version      = version,
	azure_deployment = deployment, 
	temperature      = 1,
)

def get_supabase_prompt(prompt_name: str):

    try:
        res = supabase.table(PROMPT_TABLE).select(VALUE).eq(NAME, prompt_name).single().execute()
        if res.data and VALUE in res.data:
            return res.data[VALUE]
        else:
            print(f"No data or {VALUE} found for item: {prompt_name}")
            return None
    except Exception as e:
        print(f"Error loading {prompt_name} from Supabase: {e}")
        return None
	

def get_email_enhancements(email_text: str) -> LLMRespSchema:
	try:
		# Load prompt parts from Supabase
		system_prompt = get_supabase_prompt(SYSTEM_PROMPT)
		user_context = get_supabase_prompt(USER_CONTEXT)
		json_instructions = get_supabase_prompt(JSON_INSTRUCTIONS)
		rag_context = get_relevant_context_from_rag("pozitive_scenario_1.json", NEW_EMAIL if NEW_EMAIL is not None else "")
		
		prompt = (
        f"{system_prompt}\n\n"
        f"**User Profile & Goals (JSON):**\n{json.dumps(user_context, ensure_ascii=False, indent=2)}\n\n"
        f"**Context from Past Interactions (RAG):**\n{rag_context}\n\n"
        f"**Item to Analyze (JSON Object):**\n{json.dumps(email_text, ensure_ascii=False, indent=2)}\n\n"
        f"{json_instructions}"
    )

		ai_msg = llm.invoke(prompt)
		raw = ai_msg.content
		# coalesce list→str if necessary
		if isinstance(raw, list):
			raw = "".join(str(item) for item in raw)

		# ensure we have a string to parse
		raw_str = str(raw).strip()

		decoder = json.JSONDecoder()
		try:
			# Attempt to decode the first JSON value even if there is trailing text
			obj, idx = decoder.raw_decode(raw_str)
			data = obj

		except json.JSONDecodeError:
			# Try to extract a JSON substring (object or array) using a regex fallback
			import re
			logger = logging.getLogger(__name__)
			logger.debug("Initial raw JSON decode failed, attempting regex fallback. Raw response: %s", raw_str)
			m = re.search(r'(?s)(\{.*?\}|\[.*?\])', raw_str)
			if m:
				try:
					data = json.loads(m.group(1))
				except Exception as e:
					logger.error("Regex-extracted JSON failed to parse", exc_info=e)
					return FALLBACK_RESPONSE
			else:
				logger.error("No JSON object found in LLM response")
				return FALLBACK_RESPONSE

		# Validate and coerce into the Pydantic schema
		try:
			email_enhancements: LLMRespSchema = LLMRespSchema(**data)
			return email_enhancements

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


