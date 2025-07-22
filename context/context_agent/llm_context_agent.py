
import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

# Initializarea clientului LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION", "2024-05-01-preview"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
    temperature=float(os.getenv("AZURE_TEMPERATURE", 0.2)),
)

# Instructiuni clare pentru LLM privind sarcina de procesare in batch si formatul JSON asteptat
SYSTEM_HEADER = '''You are a highly efficient AI assistant specialized in analyzing business communications.

Your task is to process a batch of items (emails, tweets, articles) and identify only the ones that are **actionable**.
An item is "actionable" if it represents a clear business opportunity, a reputational risk, a direct request, a significant update that requires a response or a specific action, or even an item that requires monitoring or acknowledgment.

For each actionable item, you must extract structured insights.

**Your output MUST be a valid JSON array of objects.**
Each object in the array represents ONE actionable item and MUST have the following structure:
- "original_item": object (The full original item from the input array)
- "analysis": object (Your analysis of the item)
  - "short_description": string (Max 50 characters, e.g., "New business lead from Solaris")
  - "actionable": boolean (This will always be `true`)
  - "opportunity_type": string (e.g., "New business opportunity", "Reputational risk", "Client request")
  - "suggested_action": string (A concrete next step, e.g., "Schedule a discovery call with Sarah Chen")
  - "relevance": string (Max 100 characters, explaining why it's important)

**CRITICAL RULES:**
1.  **FILTERING:** If an item is NOT actionable (e.g., it's a generic newsletter, a simple status update with no required action, or irrelevant marketing), you MUST ignore it and **it should NOT appear in your output array.**
2.  **JSON ONLY:** Your entire response must be a single, valid JSON array `[...]`. Do not include any text, explanations, or markdown before or after the array.
3.  **DOUBLE QUOTES:** Use only double quotes for all keys and string values in the JSON.
'''

JSON_INSTRUCTIONS = '''Based on the user profile, the historical context (RAG), and the batch of items provided, analyze each item.
Return a JSON array containing **only the actionable items** and their analysis.

Example of a valid response for a batch containing two actionable items:
[
  {
    "original_item": { ... original email object ... },
    "analysis": {
      "short_description": "Urgent request for new developer",
      "actionable": true,
      "opportunity_type": "New business opportunity",
      "suggested_action": "Source candidates for a Mid-level AI Developer with NLP skills",
      "relevance": "Client has a new, urgent hiring need due to successful expansion."
    }
  },
  {
    "original_item": { ... original twitter object ... },
    "analysis": {
      "short_description": "Public praise for partnership",
      "actionable": true,
      "opportunity_type": "Relationship building",
      "suggested_action": "Publicly reply to the tweet to thank them and reinforce the partnership",
      "relevance": "Positive public mention strengthens the brand and relationship with the client."
    }
  }
]
'''

def get_llm_analysis(user_context: dict, rag_context: str, batch_content: list) -> list:
    """
    Construieste promptul, obtine analiza de la LLM pentru un intreg batch
    si o returneaza ca lista de dictionare Python.
    """
    # Construim prompt-ul final
    prompt = (
        f"{SYSTEM_HEADER}\n\n"
        f"**User Profile & Goals (JSON):**\n{json.dumps(user_context, ensure_ascii=False, indent=2)}\n\n"
        f"**Context from Past Interactions (RAG):**\n{rag_context}\n\n"
        f"**Batch of Items to Analyze (JSON Array):**\n{json.dumps(batch_content, ensure_ascii=False, indent=2)}\n\n"
        f"{JSON_INSTRUCTIONS}"
    )

    # Structura de fallback in caz de eroare
    error_response = []
    reply = ""

    try:
        # Apelam LLM-ul si curatam raspunsul
        # Adaugam un timeout mai mare pentru procesarea batch-urilor
        response = llm.invoke(prompt, config={'timeout': 180})
        reply = response.content.strip()

        # Ne asiguram ca raspunsul este un array JSON valid
        if reply.startswith('[') and reply.endswith(']'):
            parsed = json.loads(reply)
            if isinstance(parsed, list):
                return parsed
            else:
                raise ValueError("LLM did not return a JSON array.")
        else:
            # Incercam sa extragem un array JSON din raspuns, in caz ca a adaugat text aditional
            json_match = re.search(r'\\[.*\\]', reply, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if isinstance(parsed, list):
                    return parsed
            raise ValueError("LLM response was not a valid JSON array.")

    except Exception as exc:
        print(f"❌ LLM error or invalid JSON: {exc}\n🔎 Reply was:\n{reply}")
        return error_response
