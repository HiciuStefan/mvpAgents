# analyzer/classifier.py
"""Analyzer – Tweet classifier aware of user profile **and dynamic context**.

This version adds one minimal enhancement: before sending the prompt to
Azure OpenAI, it fetches up‑to‑date context (articles & tweets) for the
**target client** via `context_api_fetcher.get_client_context()` and appends it to
the prompt.  No other behaviour is changed.

Public API:
~~~~~~~~~~~
```python
>>> from analyzer.classifier import classify_tweet, load_user_profile
>>> profile = load_user_profile("digital_excellence")
>>> classify_tweet("Looking for AI partners…", user_profile=profile, client_name="UIPath")
{'actionable': True, 'relevance': 'AI partnership opportunity', 'suggested_action': 'Contact client'}
```
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1) Azure OpenAI initialisation
# ---------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any, Dict, Optional

from llm_client import llm

# ---------------------------------------------------------------------------
# 2) Context provider import (safe‑fallback for tests)
# ---------------------------------------------------------------------------
try:
    from context_api_fetcher import get_client_context  # clarified import
except ImportError:
    def get_client_context(_: str | None) -> str:  # type: ignore
        return ""

# ---------------------------------------------------------------------------
# 3) Helpers – user profile I/O
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

# ---------------------------------------------------------------------------
# 6) CLI helper (unchanged except naming)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse, textwrap

    ap = argparse.ArgumentParser(description="Analyzer – CLI Tweet classifier")
    ap.add_argument("tweet", help="Tweet text to classify")
    ap.add_argument("--user", help="User profile JSON filename (without path)")
    ap.add_argument("--client", help="Client name for context")
    args = ap.parse_args()

    profile = load_user_profile(args.user) if args.user else None
    result = classify_tweet(args.tweet, user_profile=profile, client_name=args.client)
    print(textwrap.indent(json.dumps(result, ensure_ascii=False, indent=2), "  "))
