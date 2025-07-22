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

# Instructiuni clare pentru LLM privind sarcina de procesare a unui singur item si formatul JSON asteptat
SYSTEM_HEADER = '''You are a highly efficient AI assistant specialized in analyzing business communications.

Your task is to process a single item (email, tweet, article) and determine if it is **actionable**.
An item is "actionable" if it represents a clear business opportunity, a reputational risk, a direct request, a significant update that requires a response or a specific action, or even an item that requires monitoring or acknowledgment.

If the item is actionable, you must extract structured insights.

**Your output MUST be a single valid JSON object.**
The object represents the actionable item and MUST have the following structure:
- "original_item": object (The full original item from the input)
- "analysis": object (Your analysis of the item)
  - "short_description": string (Max 50 characters, e.g., "New business lead from Solaris")
  - "actionable": boolean (This will always be `true`)
  - "opportunity_type": string (e.g., "New business opportunity", "Reputational risk", "Client request")
  - "suggested_action": string (A concrete next step, e.g., "Schedule a discovery call with Sarah Chen")
  - "relevance": string (Max 100 characters, explaining why it's important)

**CRITICAL RULES:**
1.  **FILTERING:** If the item is NOT actionable (e.g., it's a generic newsletter, a simple status update with no required action, or irrelevant marketing), you MUST return an empty JSON object `{}`.
2.  **JSON ONLY:** Your entire response must be a single, valid JSON object. Do not include any text, explanations, or markdown before or after the object.
3.  **DOUBLE QUOTES:** Use only double quotes for all keys and string values in the JSON.
'''

JSON_INSTRUCTIONS = '''Based on the user profile, the historical context (RAG), and the item provided, analyze the item.
Return a JSON object if the item is actionable. Otherwise, return an empty JSON object.

Example of a valid response for an actionable item:
{
  "original_item": { ... original email object ... },
  "analysis": {
    "short_description": "Urgent request for new developer",
    "actionable": true,
    "opportunity_type": "New business opportunity",
    "suggested_action": "Source candidates for a Mid-level AI Developer with NLP skills",
    "relevance": "Client has a new, urgent hiring need due to successful expansion."
  }
}

Example of a valid response for a non-actionable item:
{}
'''

def get_llm_analysis_individual(user_context: dict, rag_context: str, item_content: dict) -> dict:
    """
    Construieste prompt-ul, obtine analiza de la LLM pentru un singur item
    si o returneaza ca dictionar Python.
    """
    # Construim prompt-ul final
    prompt = (
        f"{SYSTEM_HEADER}\n\n"
        f"**User Profile & Goals (JSON):**\n{json.dumps(user_context, ensure_ascii=False, indent=2)}\n\n"
        f"**Context from Past Interactions (RAG):**\n{rag_context}\n\n"
        f"**Item to Analyze (JSON Object):**\n{json.dumps(item_content, ensure_ascii=False, indent=2)}\n\n"
        f"{JSON_INSTRUCTIONS}"
    )

    # Structura de fallback in caz de eroare
    error_response = {}
    reply = ""

    try:
        # Apelam LLM-ul
        response = llm.invoke(prompt, config={'timeout': 60})
        reply = response.content.strip()

        # Ne asiguram ca raspunsul este un obiect JSON valid
        if reply.startswith('{') and reply.endswith('}'):
            parsed = json.loads(reply)
            if isinstance(parsed, dict):
                return parsed
            else:
                raise ValueError("LLM did not return a JSON object.")
        else:
            # Incercam sa extragem un obiect JSON din raspuns
            json_match = re.search(r'\{.*\}', reply, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if isinstance(parsed, dict):
                    return parsed
            raise ValueError("LLM response was not a valid JSON object.")

    except Exception as exc:
        print(f"❌ LLM error or invalid JSON: {exc}\n🔎 Reply was:\n{reply}")
        return error_response
