#!/usr/bin/env python
"""
examples/demo_tweet_classification.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Un *smoke‑test* rapid (fără pytest) care rulează `classify_tweet()` pe
4 tweet‑uri demonstrative pentru doi clienți și afișează rezultatele în
format JSON, incluzând textul tweet‑ului, flag‑ul **actionable**, câmpul
**relevance** și **suggested_action**.

Rulează‑l din rădăcina proiectului (după ce ai setat variabilele Azure
și activat venv‑ul):

```bash
$ python examples/demo_tweet_classification.py
```
"""
from __future__ import annotations

import json
from pathlib import Path

from classify_tweet import classify_tweet, load_client_profile

# ---------------------------------------------------------------------------
# 1. Load client profiles
# ---------------------------------------------------------------------------
CLIENTS = {
    "digital_excellence": load_client_profile("digital_excellence")
}

# ---------------------------------------------------------------------------
# 2. Sample tweets (same as in the pytest suite)
# ---------------------------------------------------------------------------
TWEETS: list[str] = [
    # 0 – AI / RPA
    "We're exploring AI-driven RPA solutions to streamline back-office processes. Looking for partners.",
    # 1 – MLOps
    "Looking to implement scalable MLOps pipelines to reduce model deployment time.",
    # 2 – Fasteners bulk order
    "Need bulk stainless steel M8 bolts ASAP for a maintenance shutdown next week. Any suppliers in Eastern Europe?",
    # 3 – HVAC line fasteners
    "Our HVAC assembly line needs a just-in-time fastener replenishment service. Recommendations welcome.",
    # 4 – Neutrl
    "The hard run Arne Slot will have his eye on after Liverpool’s fixtures released"
]

# ---------------------------------------------------------------------------
# 3. Run classification
# ---------------------------------------------------------------------------

def main() -> None:
    results: dict[str, list[dict[str, str | bool]]] = {}

    for client_name, profile in CLIENTS.items():
        per_client: list[dict[str, str | bool]] = []
        for tweet in TWEETS:
            classification = classify_tweet(tweet, client_profile=profile)
            per_client.append({
                "tweet": tweet,
                **classification,  # merges actionable, relevance, suggested_action
            })
        results[client_name] = per_client

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
