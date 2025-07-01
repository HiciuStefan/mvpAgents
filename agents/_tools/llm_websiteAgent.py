import json
from pathlib import Path
from typing import Any, Dict, Optional

from agents.website.context_api_fetcher import get_client_context
from .llm_client import llm

# ---------------------------------------------------------------------------
# Optional user profile loader (same as classifier)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_USER = BASE_DIR / "data" / "user"

def load_user_profile(name: str | Path) -> Dict[str, Any]:
    """Load a user JSON profile from *data/user/*."""
    path = Path(name)
    if not path.suffix:
        path = path.with_suffix(".json")
    if not path.is_absolute():
        path = DATA_USER / path.name

    with open(path, encoding="utf-8") as fp:
        return json.load(fp)

# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------
SYSTEM_HEADER = (
    "You are an AI assistant that analyzes business articles and extracts structured insights.\n\n"
    "Your task is to return a **valid JSON object** with the following fields:\n"
    "- \"short_description\": string (⚠️ max 6 words)\n"
    "- \"actionable\": boolean (true or false)\n"
    "- \"opportunity_type\": string (e.g. \"New business opportunity\")\n"
    "- \"suggested_action\": string (e.g. \"Contact client\", \"Send proposal\", \"Schedule meeting\")\n"
    "- \"relevance\": string (⚠️ max 100 characters, required only if actionable is true)\n\n"
    "⚠️ Use only double quotes in JSON.\n"
    "⚠️ Respond only with the JSON object. Do not include explanations, comments, or markdown.\n"
)


JSON_INSTRUCTIONS = (
    "Respond ONLY with a JSON object in this format (no markdown, no comments):\n"
    "{\n"
    "  \"short_description\": \"...\",\n"
    "  \"actionable\": true | false,\n"
    "  \"opportunity_type\": \"...\",\n"
    "  \"suggested_action\": \"...\",\n"
    "  \"relevance\": \"...\"\n"
    "}"
)

def _build_prompt(title: str, content: str, user_profile: Optional[Dict[str, Any]], context: str) -> str:
    user_section = (
        "User profile (JSON):\n" + json.dumps(user_profile, ensure_ascii=False, indent=2)
        if user_profile else ""
    )
    context_section = ("Recent client context:\n" + context) if context else ""

    return (
        f"{SYSTEM_HEADER}\n\n"
        f"Analyze the following article.\n\n"
        f"Title: {title}\n\n"
        f"Content:\n{content[:3000]}\n\n"
        f"{user_section}\n\n"
        f"{context_section}\n\n"
        f"{JSON_INSTRUCTIONS}"
    )

# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------
def analyze_article(
    client_name: str,
    title: str,
    content: str,
    user_profile: Optional[Dict[str, Any]] = None,
    context_provider=get_client_context
) -> Dict[str, Any]:

    context = context_provider(client_name) if client_name else ""
    prompt = _build_prompt(title, content, user_profile, context)

    try:
        reply = llm.invoke(prompt).content.strip()
        parsed = json.loads(reply)
    except Exception as exc:
        print(f"❌ LLM error or invalid JSON: {exc}\n🔎 Reply was:\n{reply}")
        return {
            "short_description": "",
            "actionable": False,
            "opportunity_type": "",
            "suggested_action": "",
            "relevance": ""
        }

    actionable = bool(parsed.get("actionable", False))

    return {
        "short_description": parsed.get("short_description", ""),
        "actionable": actionable,
        "opportunity_type": parsed.get("opportunity_type", "") if actionable else "",
        "suggested_action": parsed.get("suggested_action", "") if actionable else "",
        "relevance": parsed.get("relevance", "") if actionable else ""
    }

# ---------------------------------------------------------------------------
# CLI usage (optional test)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_client = "digital_excellence"
    profile = load_user_profile(test_client)
    result = analyze_article(
        test_client,
        "AI adoption in legal workflows",
        "UiPath unveils automation suite targeting legal departments...",
        user_profile=profile
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
