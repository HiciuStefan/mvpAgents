import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from .schema import LLMOutputItem

load_dotenv()

# Initializarea clientului LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION", "2024-05-01-preview"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
    temperature=float(os.getenv("AZURE_TEMPERATURE", 0.2)),
)

# Instructiuni aliniate cu versiunea batch, dar pentru un singur item
SYSTEM_HEADER = '''You are a highly efficient AI assistant specialized in analyzing business communications.

Your task is to process a single item (email, tweet, article), identify if it is **actionable**, and assign a priority.
An item is "actionable" if it represents a clear business opportunity, a reputational risk, a direct request, or a significant update that requires a specific action.

**Actionability Priority Levels:**
- **high**: Urgent matters. Direct business opportunities, critical reputational risks, requests with a clear deadline.
- **medium**: Important but not urgent. Non-critical client requests, opportunities needing timely follow-up.
- **low**: Requires monitoring. General updates, relationship-building notes, non-urgent acknowledgments.
- **neutral**: Not actionable. Items that do not require any action.

**Your output MUST be a single, valid JSON object.**
The object represents the item from the input and MUST have the following structure:
- "original_item": object (The full original item from the input)
- "analysis": object (Your analysis of the item)
  - "short_description": string (Max 50 characters. Summarize the item, e.g., "New business lead from Solaris" or "General news update")
  - "actionable": boolean (Set to `true` if actionable, `false` otherwise)
  - "priority_level": string (REQUIRED. One of: "high", "medium", "low", "neutral". Set to "neutral" if actionable is false.)
  - "opportunity_type": string (For actionable items: e.g., "New business opportunity", "Reputational risk", "Client request". For non-actionable items: " ")
  - "suggested_action": string (REQUIRED for actionable items: A concrete next step, e.g., "Schedule a discovery call with Sarah Chen". For non-actionable items: " ")
  - "relevance": string (Max 100 characters. REQUIRED for actionable items: explaining why it's important. For non-actionable items: " ")
  - "suggested_reply": string (REQUIRED for actionable items: A draft reply following the format rules below. For non-actionable items: " ")

**CRITICAL RULES:**
1.  **JSON ONLY:** Your entire response must be a single, valid JSON object. Do not include any text, explanations, or markdown before or after the object.
2.  **DOUBLE QUOTES:** Use only double quotes for all keys and string values in the JSON.
3.  **REPLY FORMATTING:** For the `suggested_reply` field, generate a draft in the appropriate format based on the original item's type.
4.  **REPLY STYLE:**
    - **For emails or articles:** The reply should be a professional, well-structured email.
    - **For tweets:** The reply MUST be a concise, engaging tweet under 280 characters. It should use a very informal, direct, and modern tone, like a casual conversation. It MAY include relevant hashtags or user mentions (@). **ABSOLUTELY NO email-style greetings (e.g., "Hi [Name],", "Dear [Name],") or closings (e.g., "Best regards,"). For example, a reply should NEVER start with "Hi SolarisProAi,". Think social media, not corporate email.**
    - For non-actionable items, this MUST be an empty string.
5.  **URGENT/SENSITIVE REPLIES:** If an item is classified with `priority_level: "high"` AND `opportunity_type: "Reputational risk"` or involves a similarly urgent and sensitive issue, the `suggested_reply` MUST be: "Immediate phone call required to address this sensitive issue."
'''

JSON_INSTRUCTIONS = '''Based on the user profile, the historical context (RAG), and the item provided, analyze the item.
Return a single JSON object containing the item and its analysis, following the structure defined in SYSTEM_HEADER.

Example of a valid response for an actionable item:
{
  "original_item": { ... original email object ... },
  "analysis": {
    "short_description": "Urgent request for new developer",
    "actionable": true,
    "priority_level": "high",
    "opportunity_type": "New business opportunity",
    "suggested_action": "Source candidates for a Mid-level AI Developer with NLP skills",
    "relevance": "Client has a new, urgent hiring need due to successful expansion.",
    "suggested_reply": "Hi [Client Name],\n\nThank you for reaching out..."
  }
}

Example of a valid response for a non-actionable item:
{
  "original_item": { ... original website object ... },
  "analysis": {
    "short_description": "General news update about market trends",
    "actionable": false,
    "priority_level": "neutral",
    "opportunity_type": " ",
    "suggested_action": " ",
    "relevance": " ",
    "suggested_reply": " "
  }
}
'''

def safe_print(text, prefix=""):
    """
    Safely print text that may contain Unicode characters
    """
    try:
        print(f"{prefix}{text}")
    except UnicodeEncodeError:
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(f"{prefix}{safe_text}")

def get_llm_analysis_individual(user_context: dict, rag_context: str, item_content: dict) -> dict:
    """
    Construieste promptul, obtine analiza de la LLM pentru un singur item,
    valideaza si o returneaza ca dictionar Python.
    """
    prompt = (
        f"{SYSTEM_HEADER}\n\n"
        f"**User Profile & Goals (JSON):**\n{json.dumps(user_context, ensure_ascii=False, indent=2)}\n\n"
        f"**Context from Past Interactions (RAG):**\n{rag_context}\n\n"
        f"**Item to Analyze (JSON Object):**\n{json.dumps(item_content, ensure_ascii=False, indent=2)}\n\n"
        f"{JSON_INSTRUCTIONS}"
    )

    # Structura de fallback in caz de eroare, aliniata cu logica "no-filtering"
    error_response = {
        "original_item": item_content,
        "analysis": {
            "short_description": "Analysis failed, processed as neutral",
            "actionable": False,
            "priority_level": "neutral",
            "opportunity_type": " ",
            "suggested_action": " ",
            "relevance": " ",
            "suggested_reply": " "
        }
    }
    reply = ""

    try:
        # Apelam LLM-ul
        response = llm.invoke(prompt, config={'timeout': 60})
        reply = response.content.strip()

        # Parsare robusta a JSON-ului
        json_string = reply
        json_match = re.search(r'```json\n(.*)\n```', reply, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)

        try:
            parsed_llm_output = json.loads(json_string)
            if not isinstance(parsed_llm_output, dict):
                raise ValueError("LLM did not return a JSON object.")
        except json.JSONDecodeError:
            try:
                parsed_llm_output = json.loads(reply)
                if not isinstance(parsed_llm_output, dict):
                    raise ValueError("LLM did not return a JSON object.")
            except json.JSONDecodeError:
                raise ValueError("LLM response was not a valid JSON object.")

        # --- Pydantic Validation Step ---
        try:
            validated_output = LLMOutputItem.model_validate(parsed_llm_output).model_dump()
        except ValidationError as e:
            raise ValueError(f"Pydantic validation failed: {e}")
        # --- End Pydantic Validation ---

        # Asiguram ca item-ul original din output corespunde cu cel din input
        validated_output['original_item'] = item_content

        # --- Post-processing Step ---
        analysis = validated_output.get('analysis', {})
        validated_output['analysis'] = analysis

        if analysis.get('actionable', False):
            if not analysis.get('suggested_action') or analysis.get('suggested_action').strip() == " ":
                analysis['suggested_action'] = "Review and determine next steps."
            if not analysis.get('relevance') or analysis.get('relevance').strip() == " ":
                analysis['relevance'] = "Importance requires further review."
            if not analysis.get('suggested_reply') or analysis.get('suggested_reply').strip() == " ":
                analysis['suggested_reply'] = "Review and draft a reply."
        else:
            # Asiguram ca field-urile pentru itemii non-actionabili sunt goale
            analysis['priority_level'] = "neutral"
            analysis['opportunity_type'] = analysis.get('opportunity_type', " ")
            analysis['suggested_action'] = analysis.get('suggested_action', " ")
            analysis['relevance'] = analysis.get('relevance', " ")
            analysis['suggested_reply'] = analysis.get('suggested_reply', " ")
        
        return validated_output

    except Exception as exc:
        safe_print(f"❌ LLM error or invalid JSON for item: {exc}\n🔎 Reply was:\n{reply}")
        # Returnam structura de eroare care contine item-ul original
        return error_response
