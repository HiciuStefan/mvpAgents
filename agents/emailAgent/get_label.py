import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import json


load_dotenv()

endpoint = os.getenv("ENDPOINT_URL")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
version=os.getenv("API_VERSION")
deployment = os.getenv("DEPLOYMENT_NAME")

llm = AzureChatOpenAI(
    azure_endpoint   = endpoint,   
    api_key          = subscription_key,
    api_version      = version,
    azure_deployment = deployment, 
    temperature      = 0.3,
)

def return_email_label(email_text: str,db_history_text:str) -> str:
	try:
		messages = [
			{
				"role": "system",
				"content": (
					"You are an intelligent email processor for business use. Your job is to do the classify each incoming email "
					"into one and only one of the following categories, based on the overall meaning and context of the message:\n\n"
					"{\n"
					"  \"Actionable\": The email asks the user to take a specific action such as confirming, approving, scheduling, replying, or addressing an issue. These emails usually require a response or follow-up.\n"
					"  \"Informative\": The email provides information without requiring action. It may contain updates, announcements, summaries, reports, or notifications. Often includes phrases like 'FYI', 'for your information', or 'please note'.\n"
					"  \"Invoice\": The email relates to a financial transaction. It may include terms like invoice, bill, payment, due date, amount owed, or receipt.\n"
					"  \"Contract\": The email discusses a formal agreement, legal terms, signatures, or clauses. It may include contracts, agreements, legal documents, or requests for signature.\n"
					"  \"Promo\": The email promotes products, services, or discounts. It may include marketing language like sale, offer, deal, coupon, promo, or limited-time offer.\n"
					"}\n\n"
					"Choose the single category that best describes the primary intent or topic of the email.\n"
					"Focus on the meaning of the email, not just keyword matching.\n"
					"even if you feel that this could go into muliple categories choose the most relevant one \n"
					"Add a maximum of 60 characters description of the content of the e-mail.\n"
					"An email is considered actionable if it pertains to business opportunities, product announcements, customer engagement, market signals, or collaboration.\n"
					"Set the actionable field to a boolean value (true or false, without quotes) based on this assessment.\n"
					"If the email is actionable, provide both a suggested action (max 40 characters) and a brief explanation of why the email is relevant (max 100 characters).\n"
					"If the email is not actionable, set both suggested_action and relevance to empty strings (\"\").\n"
                    "Return your answer in the following JSON format:\n"
					"{\n"
					"  \"category\": \"Actionable\",\n"
					"  \"short_description\": \"A complaint from a customer\",\n"
					"  \"actionable\": true,\n"
					"  \"suggested_action\": \"View invoice.\",\n"
					"  \"relevance\": \"Contract changes might risk project delays if not followed up promptly.\"\n"
					"}\n\n"
					"Only return the JSON. Do not include any explanation or additional content."
				)
			},
			{
        		"role": "user",
        		"content": "Historical Emails:\n" + db_history_text
			},
			{
				"role": "user",
				"content": "New Email:\n" + email_text
			}
		]

		ai_msg = llm.invoke(messages)

		result = json.loads(ai_msg.content)
		return result

	except Exception as e:
		print(f"Error processing email text: {e}")
		# Return a fallback dictionary 
		return {
			"category": "Unknown",
			"short_description": "",
			"suggested_action": ""
		}


