import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from docx_reader import DocxReader

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Inițializează modelul LLM
# llm = ChatOpenAI(
# 	temperature=0.7,
# 	model="gpt-4o-mini",
# 	openai_api_key=api_key
# )


if "AZURE_OPENAI_API_KEY" not in os.environ:
	os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
		"Enter your AzureOpenAI API key: "
	)
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://openai-vasi.openai.azure.com/openai/deployments/gpt-35-turbo-vasi/chat/completions?api-version=2025-01-01-preview"

llm = AzureChatOpenAI(
	azure_deployment="gpt-35-turbo-vasi",  # or your deployment
	api_version="2025-01-01-preview",  # or your api version
	temperature=0,
	max_tokens=None,
	timeout=None,
	max_retries=2,
	# other params...
)


# llm = ChatOpenAI(
# 	temperature=0.7,
# 	openai_api_base="http://192.168.1.224:1234/v1",
# 	model="gemma-3-1b-it-qat"
# )

reader = DocxReader("contracte/2.docx");



import fitz  # PyMuPDF

file_path = "contracte/Contract1.pdf"

def read_pdf_text(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

# Example
all_text = read_pdf_text("contracte/Contract1.pdf")


#1.224:1234
# gemma-3-1b-it-qat

def generate_reply(tweet_text: str) -> str:
	"""
	Generează un răspuns scurt și prietenos pentru un tweet.
	"""
	prompt = f"""You are a helpful AI assistant that writes thoughtful, concise Twitter replies.
Tweet: "{tweet_text}"
Reply:"""
	try:
		messages = [
			(
				"system",
				"You are a helpful assistant that interprets contracts between my company and my partners. Please extract me the data out of that contract and list them in a formated type, like a json",
			),
			(all_text),
		]

		messages = [
			{
				"role": "system",
				"content": (
					"You are an intelligent email processor for business use. Your job is to classify incoming emails "
					"into one or more of the following categories, based on the presence of relevant keywords or context:\n\n"
					"{\n"
					"  \"Work\": [\"meeting\", \"project\", \"client\", \"deadline\", \"task\"],\n"
					"  \"Urgent\": [\"urgent\", \"ASAP\", \"immediate\", \"important\", \"response needed\"],\n"
					"  \"Invoice\": [\"invoice\", \"payment\", \"due\", \"bill\", \"receipt\"],\n"
					"  \"Contract\": [\"contract\", \"agreement\", \"terms\", \"sign\", \"clause\", \"legal\"],\n"
					"  \"Promo\": [\"sale\", \"discount\", \"offer\", \"promo\", \"coupon\", \"deal\"]\n"
					"}\n\n"
					"2. Decide if the email requires a reply based on whether the sender explicitly asks for a response, "
            "follow-up, or action from the recipient.\n\n"
            "Return your answer in the following JSON format:\n"
            "{\n"
            "  \"categories\": [\"Work\", \"Urgent\"],\n"
            "  \"should_reply\": true / false\n"
			"  \"is_urgent\": true false\n"
            "}"
					"Only return the JSON. Classify based on meaning, not just keyword matching."
				)
			},
			{
				"role": "user",
				"content": """
				Hi There,

My name is Fatima, and I am the Director of Customer Success at Beautiful.ai. I noticed you haven’t been active in a while, so I thought I’d check in.

I’d love to hear about your experience if you’re interested in providing some feedback. You can share by responding to me directly or taking this one minute survey.

I really appreciate your time and insights! Your feedback helps us build a better product. Thank you for your help in democratizing design."""
			}
		]
		ai_msg = llm.invoke(messages)
		# ai_msg

		return ai_msg.content



		# response = llm.invoke(prompt)
		# print(response)
		# return response.content.strip()
	except Exception as e:
		print(f"❌ Eroare la generarea răspunsului GPT: {e}")
		return "Thank you for sharing your thoughts!"

print(generate_reply('some shit'));



