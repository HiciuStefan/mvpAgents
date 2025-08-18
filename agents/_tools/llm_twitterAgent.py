# generate_summary.py

from agents._tools.llm_client import llm
from typing import Optional, Dict, Any
import json
from pathlib import Path
from agents.common.context_api_fetcher import get_client_context


from agents.config.config_loader import load_user_profile

# ---------------------------------------------------------------------------
# 4) Prompt building (includes client context)
# ---------------------------------------------------------------------------
SYSTEM_HEADER = (
    "You are a highly efficient AI assistant specialized in analyzing tweets for business actionability.\n"
    "Your goal is to determine whether the tweet is actionable and produce a compact analysis with the fields below."
)

JSON_INSTRUCTIONS = (
    "Respond ONLY with a single JSON object using DOUBLE QUOTES for all strings/keys. No markdown, no extra text.\n"
    "The JSON object MUST have EXACTLY these keys:\n"
    "{\n"
    "  \"short_description\": \"Max 50 characters\",\n"
    "  \"actionable\": true | false,\n"
    "  \"priority_level\": \"high|medium|low|neutral\",\n"
    "  \"opportunity_type\": \"For actionable items (e.g., New business opportunity). For non-actionable: \u0020\",\n"
    "  \"suggested_action\": \"For actionable items: a concrete next step. For non-actionable: \u0020\",\n"
    "  \"relevance\": \"For actionable: why it matters (<=100 chars). For non-actionable: \u0020\",\n"
    "  \"suggested_reply\": \"For actionable: a short tweet reply. For non-actionable: \u0020\"\n"
    "}\n\n"
    "Rules:\n"
    "- If actionable is false, set priority_level to \"neutral\" and use a single space (\u0020) for opportunity_type, suggested_action, relevance, suggested_reply.\n"
    "- The suggested_reply must be formatted as a tweet when actionable is true.\n"
    "- Output must be valid JSON with only the keys above."
)


def _build_prompt(
    tweet_text: str,
    user_profile: Optional[Dict[str, Any]],
    fetched_context: str = "",
) -> str:
    """Assemble the full prompt string."""

    user_section = (
        "User profile (JSON):\n" + json.dumps(user_profile, ensure_ascii=False, indent=2)
        if user_profile
        else ""
    )

    context_section = (
        "Recent client context:\n" + fetched_context if fetched_context else ""
    )

    return (
        f"{SYSTEM_HEADER}\n\n"
        "Decide if the tweet is actionable for this specific user.\n"
        "A tweet is actionable if it relates to the user's industries, products, services, goals, ICP, or a clear business opportunity.\n\n"
        f"{user_section}\n\n"
        f"{context_section}\n\n"
        f"Tweet: \"{tweet_text}\"\n\n"
        f"{JSON_INSTRUCTIONS}"
    )

# ---------------------------------------------------------------------------
# 5) Public function – uses user profile and client name for context
# ---------------------------------------------------------------------------

def classify_tweet(
    tweet_text: str,
    *,
    user_profile: Optional[Dict[str, Any]] = None,
    client_name: Optional[str] = None,
    context_provider=get_client_context,
) -> Dict[str, Any]:
    """Analyze the tweet and return fields aligned with llm_context_agent's analysis schema."""

    # Load user profile if not provided (best-effort)
    if user_profile is None:
        try:
            user_profile = load_user_profile()
        except Exception:
            user_profile = None

    fetched_context = context_provider(client_name) if client_name else ""
    prompt = _build_prompt(tweet_text, user_profile, fetched_context)

    raw_reply = ""
    try:
        response = llm.invoke(prompt)
        raw_content = response.content
        raw_reply = raw_content if isinstance(raw_content, str) else json.dumps(raw_content, ensure_ascii=False)
        json_string = raw_reply
        # Extract fenced json if present
        if json_string.startswith("```"):
            start = json_string.find("```json")
            end = json_string.rfind("```")
            if start != -1 and end != -1 and end > start:
                json_string = json_string[start + len("```json"):end].strip()
            elif json_string.startswith("```") and json_string.endswith("```"):
                json_string = json_string.strip("`").strip()
        parsed = json.loads(json_string)
    except Exception as exc:
        print(f"⚠️  classify_tweet error: {exc}\n🔎 Reply was:\n{raw_reply}")
        parsed = {}

    # Ensure dict structure
    if not isinstance(parsed, dict):
        parsed = {}

    # Normalize fields and apply defaults consistent with llm_context_agent
    actionable = bool(parsed.get("actionable", False))
    short_description = parsed.get("short_description") or (tweet_text[:47] + "..." if len(tweet_text) > 50 else tweet_text)
    priority_level = parsed.get("priority_level") or ("neutral" if not actionable else "low")
    opportunity_type = parsed.get("opportunity_type")
    suggested_action = parsed.get("suggested_action")
    relevance = parsed.get("relevance")
    suggested_reply = parsed.get("suggested_reply")

    if actionable:
        if not suggested_action or suggested_action.strip() == "":
            suggested_action = "Review and determine next steps."
        if not relevance or relevance.strip() == "":
            relevance = "Importance requires further review."
        if not suggested_reply or suggested_reply.strip() == "":
            suggested_reply = "Thank you for the update!"
        if not opportunity_type or opportunity_type.strip() == "":
            opportunity_type = "General business opportunity"
    else:
        priority_level = "neutral"
        opportunity_type = " "
        suggested_action = " "
        relevance = " "
        suggested_reply = " "

    return {
        "short_description": short_description[:50],
        "actionable": actionable,
        "priority_level": priority_level,
        "opportunity_type": opportunity_type,
        "suggested_action": suggested_action,
        "relevance": relevance,
        "suggested_reply": suggested_reply,
    }


def generate_summary(tweet_text: str) -> str:
    """
    Primește un tweet și returnează un sumar scurt de 5-6 cuvinte.
    """
    prompt = f"""Summarize the following tweet in 5-6 words maximum.
Tweet: "{tweet_text}"
Summary:"""

    try:
        result = llm.invoke(prompt)
        content = result.content
        return content.strip() if isinstance(content, str) else str(content)
    except Exception as e:
        return f"(Error: {e})"

def generate_reply(tweet_text: str) -> str:
    """
    Generează un răspuns scurt și prietenos pentru un tweet.
    """
    prompt = f"""You are a helpful AI assistant that writes thoughtful, concise Twitter replies.
Tweet: "{tweet_text}"
Reply:"""
    try:
        response = llm.invoke(prompt)
        content = response.content
        return content.strip() if isinstance(content, str) else str(content)
    except Exception as e:
        print(f"❌ Eroare la generarea răspunsului GPT: {e}")
        return "Thank you for sharing your thoughts!"

