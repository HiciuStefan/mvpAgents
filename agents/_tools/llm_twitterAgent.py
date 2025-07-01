# generate_summary.py

from llm_client import llm
from typing import Optional, Dict, Any
import json
from agents.twitter.context_api_fetcher import get_client_context


      
# ---------------------------------------------------------------------------
# 4) Prompt building (includes client context)
# ---------------------------------------------------------------------------
SYSTEM_HEADER = (
    "You are an AI assistant that analyzes tweets to determine whether they "
    "are actionable for a specific business user."
)

JSON_INSTRUCTIONS = (
    "Respond **only** with a JSON object like this (no markdown, no extra keys):\n"
    "{\n  \"actionable\": true | false,\n  \"relevance\": \"...\",\n  \"suggested_action\": \"...\"\n}"
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
        "Step 1 – Decide if the tweet is actionable **for this specific user**. "
        "A tweet is actionable if it relates to any of the user's industries, "
        "products, services, goals, ICP or clear business opportunities.\n\n"
        "Step 2 – If actionable, answer:\n"
        "- What is the business relevance of this tweet? (max 100 chars)\n"
        "- What is the suggested action? (e.g. \"Contact client\")\n\n"
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
    """Classify tweet as actionable / not‑actionable for a user with respect to a given client."""

    fetched_context = context_provider(client_name) if client_name else ""

    prompt = _build_prompt(tweet_text, user_profile, fetched_context)

    try:
        reply = llm.invoke(prompt).content.strip()
        parsed = json.loads(reply)
    except Exception as exc:
        print(f"⚠️  classify_tweet error: {exc}")
        return {"actionable": False, "relevance": "", "suggested_action": ""}

    if not isinstance(parsed, dict):
        return {"actionable": False, "relevance": "", "suggested_action": ""}

    actionable = bool(parsed.get("actionable", False))
    return {
        "actionable": actionable,
        "relevance": parsed.get("relevance", "") if actionable else "",
        "suggested_action": parsed.get("suggested_action", "") if actionable else "",
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
        return result.content.strip()
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
        return response.content.strip()
    except Exception as e:
        print(f"❌ Eroare la generarea răspunsului GPT: {e}")
        return "Thank you for sharing your thoughts!"

