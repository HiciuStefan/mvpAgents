import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from tools import get_all_files, read_pdf_text, read_docx_text


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

#1.224:1234
# gemma-3-1b-it-qat


const = """
You are a helpful assistant that extracts key legal and business information
from Romanian contracts between a company and its partners.

Please extract the following fields from the contract and return them in JSON format.

- Numele complet al clientului.
- Cod Unic de Înregistrare (CUI).
- Adresa sediului firmei.
- Reprezentantul legal menționat în contract.
- Data semnării contractului și durata acestuia.
- Valoarea contractului și moneda.

Rules:
- My company is "Mobile Excellence". I always want the other company's details.


"Format your response as follows:\n"
{
	"nume_firma": ...,
	"cui": ...,
	"adresa_sediu": ...,
	"reprezentant_legal": ...,
	"data_semnare": ...,
	"durata_contract" {
		start_date: the start date of the contract
		end_date: if availale, else make it null
		length: if available, else make it null
	},
	"contract_value": {
		"type": type is proabbly one of 'hourly', 'daily', or 'total' depending on how the value is defined,"
		"value": main payment amount value (i want an integer),
		"currency": the currency of the contract value
	}
}
"""



 

def generate_reply(text: str) -> str:
	try:
		messages = [{
			"role": "system",
			"content": const
		}, {
			"role": "user",
			"content": text
		}]
		ai_msg = llm.invoke(messages)

		return ai_msg.content

		# response = llm.invoke(prompt)
		# print(response)
		# return response.content.strip()
	except Exception as e:
		print(f"❌ Eroare la generarea răspunsului GPT: {e}")
		return "Thank you for sharing your thoughts!"



FOLDER_NAME='downloads'

def get_all():
	files = get_all_files(FOLDER_NAME)
	processed = []
	for file in files:
		if file.lower().endswith((".docx", ".pdf")):
			content = get_file_contents(file)
			data = generate_reply(content)
			processed.append(data)

	return processed



def get_file_contents(file_name: str) -> str:
	data = ''
	if file_name.lower().endswith(".pdf"):
		data = read_pdf_text(file_name)
	if file_name.lower().endswith('.docx'):
		data = read_docx_text(file_name)

	return data