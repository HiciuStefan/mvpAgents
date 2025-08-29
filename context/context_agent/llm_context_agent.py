
import os
import json
import re
import sys
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from .schema import LLMOutputItem

load_dotenv()

# Initializarea clientului LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION", "2024-01-01-preview"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
    # temperature=float(os.getenv("AZURE_TEMPERATURE", 0.2)),
)

# Instructiuni clare pentru LLM privind sarcina de procesare in batch si formatul JSON asteptat
SYSTEM_HEADER = '''You are a highly efficient AI assistant specialized in analyzing business communications.

Your task is to process a batch of items (emails, tweets, articles), identify the **actionable** ones, and assign a priority.
An item is "actionable" if it represents a clear business opportunity, a reputational risk, a direct request, or a significant update that requires a specific action.

**Actionability Priority Levels:**
- **high**: Urgent matters. Direct business opportunities, critical reputational risks, requests with a clear deadline.
- **medium**: Important but not urgent. Non-critical client requests, opportunities needing timely follow-up.
- **low**: Requires monitoring. General updates, relationship-building notes, non-urgent acknowledgments.
- **neutral**: Not actionable. Items that do not require any action.

**Your output MUST be a valid JSON array of objects.**
Each object in the array represents ONE item from the input batch and MUST have the following structure:
- "original_item": object (The full original item from the input array)
- "analysis": object (Your analysis of the item)
  - "short_description": string (Max 50 characters. Summarize the item, e.g., "New business lead from Solaris" or "General news update")
  - "actionable": boolean (Set to `true` if actionable, `false` otherwise)
  - "priority_level": string (REQUIRED. One of: "high", "medium", "low", "neutral". Set to "neutral" if actionable is false.)
  - "opportunity_type": string (For actionable items: e.g., "New business opportunity", "Reputational risk", "Client request". For non-actionable items: " ")
  - "suggested_action": string (REQUIRED for actionable items: A concrete next step, e.g., "Schedule a discovery call with Sarah Chen". For non-actionable items: " ")
  - "relevance": string (Max 100 characters. REQUIRED for actionable items: explaining why it's important. For non-actionable items: " ")
  - "suggested_reply": string (REQUIRED for actionable items: A draft reply following the format rules below. For non-actionable items: " ")

**CRITICAL RULES:**
1.  **ABSOLUTELY NO FILTERING:** You MUST include ALL items from the input batch in your output array. Do NOT omit any items.
2.  **JSON ONLY:** Your entire response must be a single, valid JSON array `[...]`. Do not include any text, explanations, or markdown before or after the array.
3.  **DOUBLE QUOTES:** Use only double quotes for all keys and string values in the JSON.
4.  **REPLY FORMATTING:** For the `suggested_reply` field, generate a draft in the appropriate format based on the original item's type.
5.  **REPLY STYLE:**
    - **For emails or articles:** The reply should be a professional, well-structured email.
    - **For tweets:** The reply MUST be a concise, engaging tweet under 280 characters. It should use a very informal, direct, and modern tone, like a casual conversation. It MAY include relevant hashtags or user mentions (@). **ABSOLUTELY NO email-style greetings (e.g., "Hi [Name],", "Dear [Name],") or closings (e.g., "Best regards,"). For example, a reply should NEVER start with "Hi SolarisProAi,". Think social media, not corporate email.**
    - For non-actionable items, this MUST be an empty string.
6.  **URGENT/SENSITIVE REPLIES:** If an item is classified with `priority_level: "high"` AND `opportunity_type: "Reputational risk"` or involves a similarly urgent and sensitive issue, the `suggested_reply` MUST be: `"Immediate phone call required to address this sensitive issue."`
'''

JSON_INSTRUCTIONS = '''Based on the user profile, the historical context (RAG), and the batch of items provided, analyze each item.
Return a JSON array containing **ALL items from the input batch**, including both actionable and non-actionable ones, and their analysis, following the structure defined in SYSTEM_HEADER.

Example of a valid response for a batch containing three items (one high actionable, one low actionable, one non-actionable):
[
  {
    "original_item": { ... original email object ... },
    "analysis": {
      "short_description": "Urgent request for new developer",
      "actionable": true,
      "priority_level": "high",
      "opportunity_type": "New business opportunity",
      "suggested_action": "Source candidates for a Mid-level AI Developer with NLP skills",
      "relevance": "Client has a new, urgent hiring need due to successful expansion.",
      "suggested_reply": "Hi [Client Name],

Thank you for reaching out. We understand the urgency and are happy to help. We are starting the search for a Mid-level AI Developer with NLP skills immediately and will send you the first batch of qualified candidates within the next 48 hours.

Best regards,
[Your Name]"
    }
  },
  {
    "original_item": { ... original twitter object ... },
    "analysis": {
      "short_description": "Public praise for partnership",
      "actionable": true,
      "priority_level": "low",
      "opportunity_type": "Relationship building",
      "suggested_action": "Publicly reply to the tweet to thank them and reinforce the partnership",
      "relevance": "Positive public mention strengthens the brand and relationship with the client.",
      "suggested_reply": "@[Client's Twitter Handle] We're thrilled to have you as a partner! Thank you for the kind words. Looking forward to achieving great things together. #Partnership #Success"
    }
  },
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
]
'''

def safe_print(text, prefix=""):
    """
    Safely print text that may contain Unicode characters
    """
    try:
        print(f"{prefix}{text}")
    except UnicodeEncodeError:
        # Fallback: encode with replacement characters
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(f"{prefix}{safe_text}")

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
        response = llm.invoke(prompt, config={"timeout": 180})
        reply = response.content.strip()

        parsed_llm_output = []
        json_string = reply

        # Incercam sa extragem un array JSON din raspuns, in caz ca a adaugat text aditional (e.g., ```json...```)
        json_match = re.search(r'```json\n(.*)\n```', reply, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
        
        try:
            parsed_llm_output = json.loads(json_string)
            if not isinstance(parsed_llm_output, list):
                raise ValueError("LLM did not return a JSON array.")
        except json.JSONDecodeError:
            # Daca nu a fost un bloc de cod sau parsarea a esuat, incercam sa parsam direct raspunsul
            try:
                parsed_llm_output = json.loads(reply)
                if not isinstance(parsed_llm_output, list):
                    raise ValueError("LLM did not return a JSON array.")
            except json.JSONDecodeError:
                raise ValueError("LLM response was not a valid JSON array.")

        # --- Pydantic Validation Step ---
        try:
            # Validate each item in the parsed list. .model_dump() ensures the rest of the function gets a dict.
            validated_output = [LLMOutputItem.model_validate(item).model_dump() for item in parsed_llm_output]
            parsed_llm_output = validated_output # Replace the original list with the validated one
        except ValidationError as e:
            # If validation fails, we raise an error to be caught by the outer exception handler.
            raise ValueError(f"Pydantic validation failed: {e}")
        # --- End Pydantic Validation ---

        # Create a lookup for LLM-analyzed items based on their original_item content
        llm_output_map = {}
        for item in parsed_llm_output:
            if 'original_item' in item:
                original_item_from_llm = item['original_item']
                key = (original_item_from_llm.get('type'), original_item_from_llm.get('body') or original_item_from_llm.get('content') or original_item_from_llm.get('text'))
                llm_output_map[key] = item

        final_results = []
        for original_input_item in batch_content:
            original_item_key = (original_input_item.get('type'), original_input_item.get('body') or original_input_item.get('content') or original_input_item.get('text'))
            
            if original_item_key in llm_output_map:
                # If LLM analyzed this item, use its analysis
                item_with_analysis = llm_output_map[original_item_key]
            else:
                # If LLM did not analyze this item, create a default neutral analysis
                item_with_analysis = {
                    "original_item": original_input_item,
                    "analysis": {
                        "short_description": "General update - neutral",
                        "actionable": False,
                        "opportunity_type": " ",
                        "suggested_action": " ",
                        "relevance": " ",
                        "suggested_reply": " "
                    }
                }
            
            # Post-processing: Ensure suggested_action and relevance are completed for actionable items
            analysis = item_with_analysis.get('analysis', {})
            item_with_analysis['analysis'] = analysis # Ensure analysis dict exists

            if analysis.get('actionable', False):
                if not analysis.get('suggested_action') or analysis.get('suggested_action').strip() == " ":
                    analysis['suggested_action'] = "Review and determine next steps."
                if not analysis.get('relevance') or analysis.get('relevance').strip() == " ":
                    analysis['relevance'] = "Importance requires further review."
                if not analysis.get('suggested_reply') or analysis.get('suggested_reply').strip() == " ":
                    analysis['suggested_reply'] = "Review and draft a reply."
            else:
                # Ensure non-actionable items have empty strings for these fields
                analysis['opportunity_type'] = analysis.get('opportunity_type', " ")
                analysis['suggested_action'] = analysis.get('suggested_action', " ")
                analysis['relevance'] = analysis.get('relevance', " ")
                analysis['suggested_reply'] = analysis.get('suggested_reply', " ")
            
            final_results.append(item_with_analysis)
        
        return final_results

    except Exception as exc:
        safe_print(f"❌ LLM error or invalid JSON: {exc}\n🔎 Reply was:\n{reply}")
        return error_response

