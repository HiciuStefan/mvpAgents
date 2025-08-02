import json
from datetime import datetime, timezone
import uuid

# --- Function copied directly from payload_builder.py for isolated testing ---
def build_dashboard_payload(item: dict, analysis: dict) -> dict:
    source_type = item.get("type", "unknown")
    llm_analysis = analysis.get("analysis", {})
    if not isinstance(llm_analysis, dict):
        llm_analysis = {}
        
    payload = {}

    if source_type == "tweet":
        payload = {
            "url": item.get("url", "https://twitter.com/placeholder/status/12345"),
            "text": item.get("content", "No content provided"),
            "actionable": True,
            "client_name": "SolarisProAi",
            "tweet_id": item.get("tweet_id", "123456789"),
            "relevance": llm_analysis.get("relevance", "unknown"),
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "status": "new",
            "reply": ""
        }

    if payload:
        required_fields = ["url", "text", "actionable", "relevance", "suggested_action", "short_description", "client_name", "status", "reply", "tweet_id"]
        
        print("--- DEBUG: Payload content before validation ---")
        print(json.dumps(payload, indent=2))

        for field in required_fields:
            if payload.get(field) is None:
                print(f"  -> DEBUG: Validation failed. Required field '{field}' is missing or None.")
                return {}, source_type

    return payload, source_type
# --- End of copied function ---

# 1. Sample Twitter item
test_tweet_item = {
    "type": "twitter",
    "content": "This is a test tweet!"
}

# 2. Mock analysis from LLM
mock_analysis = {
    "analysis": {
        "short_description": "Test tweet - high",
        "suggested_action": "Test action",
        "relevance": "Test relevance"
    }
}

# 3. Call the function
payload, source_type = build_dashboard_payload(test_tweet_item, mock_analysis)

# 4. Print the final output
print("\n--- Final Generated Payload ---")
print(json.dumps(payload, indent=2))

if not payload:
    print("\n--- Result ---")
    print("🔴 The payload is EMPTY.")
else:
    print("\n--- Result ---")
    print("🟢 The payload was generated successfully.")