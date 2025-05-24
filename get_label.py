import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
import json


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

AZURE_OPENAI_API_KEY="ACYhswv9bdG9HLSwegzWBaepqA7mKYn3mQtHqU3hiTJzzbRO9qyOJQQJ99BEACfhMk5XJ3w3AAABACOGp1TG"
if "AZURE_OPENAI_API_KEY" not in os.environ:
	os.environ["AZURE_OPENAI_API_KEY"] = "ACYhswv9bdG9HLSwegzWBaepqA7mKYn3mQtHqU3hiTJzzbRO9qyOJQQJ99BEACfhMk5XJ3w3AAABACOGp1TG"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://openai-vasi.openai.azure.com/openai/deployments/gpt-35-turbo-vasi/chat/completions?api-version=2025-01-01-preview"

llm = AzureChatOpenAI(
	azure_deployment="gpt-35-turbo-vasi",  # or your deployment
	api_version="2025-01-01-preview",  # or your api version
	temperature=0,
	max_tokens=None,
	timeout=None,
	max_retries=2,

)

def return_email_label(email_text: str) -> str:
	try:
		messages = [
			{
				"role": "system",
				"content": (
					"You are an intelligent email processor for business use. Your job is to classify each incoming email "
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
					"Return your answer in the following JSON format:\n"
					"{\n"
					"  \"category\": \"Actionable\"\n"
					"}\n\n"
					"Only return the JSON. Do not include any explanation or additional content."
				)
			},
			{
				"role": "user",
				"content": email_text
			}
		]

		ai_msg = llm.invoke(messages)

		result = json.loads(ai_msg.content)
		return result["category"]

	except Exception as e:
		print(f"❌ Eroare la generarea răspunsului GPT: {e}")
		return "Thank you for sharing your thoughts!"


