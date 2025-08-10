from datetime import datetime, timezone
import json
import uuid

def safe_get(d, key, default):
    value = d.get(key, default)
    return value if value is not None else default

def build_dashboard_payload(item: dict, analysis: dict) -> tuple[dict, str]:
    """
    Construieste payload-ul specific pentru dashboard pe baza tipului de item.
    """
    source_type = item.get("type", "unknown")
    llm_analysis = analysis
    if not isinstance(llm_analysis, dict):
        llm_analysis = {}

    # Maparea nivelului de prioritate la o valoare numerica de urgenta
    priority_mapping = {
        "neutral": 0,
        "low": 1,
        "medium": 2,
        "high": 3
    }
    priority_level = safe_get(llm_analysis, "priority_level", "neutral")
    urgency = priority_mapping.get(priority_level, 0)

    payload = {}

    # Logica pentru email (functioneaza)
    if source_type == "email":
        payload = {
            "content": item.get("body", "No content provided"),
            "client_name": "SolarisProAi",
            "type": source_type,
            "message_id": safe_get(item, "message_id", str(uuid.uuid4())),
            "subject": item.get("subject", "No Subject"),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "actionable": llm_analysis.get("actionable", False),
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "suggested_reply": llm_analysis.get("suggested_reply", ""),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "relevance": llm_analysis.get("relevance", "unknown"),
            "urgency": urgency
        }
    
    # Logica reconstruita pentru twitter, urmand modelul celorlalte
    elif source_type == "twitter":
        payload = {
            "url": safe_get(item, "url", "https://twitter.com/unknown/status/00000"),
            "text": safe_get(item, "content", "No content provided"),
            "tweet_id": safe_get(item, "tweet_id", "000000000"),
            "actionable": llm_analysis.get("actionable", False),
            "client_name": "SolarisProAi",
            "relevance": safe_get(llm_analysis, "relevance", "unknown"),
            "suggested_action": safe_get(llm_analysis, "suggested_action", "No specific action suggested"),
            "suggested_reply": llm_analysis.get("suggested_reply", ""),
            "short_description": safe_get(llm_analysis, "short_description", "No description provided"),
            "urgency": urgency
        }
        
    # Logica pentru website (functioneaza)
    elif source_type == "website":
        payload = {
            "client_name": item.get("client_name", "SolarisProAi"),
            "url": item.get("url", ""),
            "title": item.get("title", "No Title"),
            "content": item.get("content", "No content provided"),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "actionable": llm_analysis.get("actionable", False),
            "opportunity_type": llm_analysis.get("opportunity_type", "unknown"),
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "suggested_reply": llm_analysis.get("suggested_reply", ""),
            "relevance": llm_analysis.get("relevance", "unknown"),
            "read": False,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "urgency": urgency
        }

    # Logica de validare (functioneaza pentru email si website)
    return payload, source_type

def test_twitter_payload():
    item = {
        "type": "twitter",
        "date": "2024-09-07",
        "title": "Team Expansion Pause",
        "content": "Taking a short breather as we onboard our latest team additions. Stability and alignment are just as important as rapid growth. #AIExpansion #GrowthPacing",
        # intentionally omit 'url' and 'tweet_id' to test defaults
        # 'reply' is not used in payload construction
    }
    analysis = {
        "priority_level": "medium",
        "short_description": "Team expansion pause - medium"
    }
    payload, source_type = build_dashboard_payload(item, analysis)
    print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
    print("Source type:", source_type)

if __name__ == "__main__":
    test_twitter_payload()
