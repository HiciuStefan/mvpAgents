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
from agents._tools.llm_twitterAgent import classify_tweet



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
