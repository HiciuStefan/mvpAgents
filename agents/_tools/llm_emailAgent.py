import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, SecretStr, ValidationError
import json
from supabase import create_client, Client

PROMPT_TABLE= "Prompt"
PROMPT_NAME = "prompt_name"
PROMPT_PAYLOAD = "prompt_payload"
SYSTEM_USER_CONTEXT_PROMP = "system_user_context_prompt"

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

def load_prompt_from_supabase(prompt: str):
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

def get_email_enhancements(email_text: str, db_history_text: str) -> LLMRespSchema:
	try:
		# messages = [
		# 	{
		# 		"role": "system",
		# 		"content": (
		# 				"You are an intelligent email processor for business use. "
		# 				"Analyze the provided email and return ONLY a valid JSON object "
		# 				"with the following fields:\n\n"

		# 				"1. short_description (string, max 60 characters): "
		# 				"A concise summary of the email content.\n"
		# 				"2. actionable (boolean): true or false (no quotes). "
		# 				"An email is actionable if it meets ANY of these criteria:\n"
		# 				"   - Pertains to business opportunities\n"
		# 				"   - Contains product announcements\n"
		# 				"   - Involves customer engagement\n"
		# 				"   - Provides market signals\n"
		# 				"   - Requests or proposes collaboration\n"
		# 				"If unsure, set actionable to false.\n"
		# 				"3. suggested_action (string, max 40 characters): "
		# 				"If actionable=true, a concise next step that directly relates to the content of the email. "
		# 				"If actionable=false, set to \"\".\n"
		# 				"4. relevance (string, max 100 characters): "
		# 				"If actionable=true, explain why the email matters. "
		# 				"If actionable=false, set to \"\".\n"
		# 				"5. suggested_reply (string): A polite, professional reply to the email.\n\n"

		# 				"Formatting rules:\n"
		# 				"- Output must be valid JSON with double quotes around all keys and string values.\n"
		# 				"- No trailing commas.\n"
		# 				"- Do not include any text outside the JSON.\n\n"

		# 				"Example output:\n"
		# 				"{\n"
		# 				"  \"short_description\": \"A complaint from a customer\",\n"
		# 				"  \"actionable\": true,\n"
		# 				"  \"suggested_action\": \"View invoice.\",\n"
		# 				"  \"relevance\": \"Contract changes might risk project delays if not followed up promptly.\",\n"
		# 				"  \"suggested_reply\": \"Thank you for your email. We apologize for the inconvenience caused. We are looking into the issue and will get back to you shortly with a resolution. Your satisfaction is our priority.\"\n"
		# 				"}\n\n"

		# 				"ONLY return the JSON object. Do not include explanations, notes, or extra text."

		# 		)
		# 	},
		# 	{
		# 		"role": "user",
		# 		"content": "Historical Emails:\n" + db_history_text
		# 	},
		# 	{
		# 		"role": "user",
		# 		"content": "New Email:\n" + email_text
		# 	}
		# ]

		# Optionally load prompt from Supabase and override only if valid
		supabase_prompt = load_prompt_from_supabase(SYSTEM_USER_CONTEXT_PROMP)
		if supabase_prompt is None:
			return FALLBACK_RESPONSE
		else:	
			messages = supabase_prompt

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


