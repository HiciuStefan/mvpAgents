from datetime import datetime, timezone
import json
import uuid

def build_dashboard_payload(item: dict, analysis: dict) -> dict:
    """
    Construieste payload-ul specific pentru dashboard pe baza tipului de item.
    """
    source_type = item.get("type", "unknown")
    llm_analysis = analysis.get("analysis", {})
    payload = {}

    

    if source_type == "email":
        payload = {
            "content": item.get("body", "No content provided"),
            "client_name": "SolarisProAi",
            "type": source_type, # Use source_type for consistency
            "message_id": str(uuid.uuid4()), # Generate a unique ID
            "subject": item.get("subject", "No Subject"),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "actionable": True,
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "relevance": llm_analysis.get("relevance", "unknown")
        }
    elif source_type == "tweet":
        payload = {
            "url": item.get("url", f"https://twitter.com/someuser/status/{uuid.uuid4()}"), # Generate a more realistic placeholder URL if not present
            "text": item.get("content", "No content provided"),
            "actionable": True, # Always True for actionable tweets
            "client_name": "SolarisProAi",
            "tweet_id": item.get("tweet_id", str(uuid.uuid4())),
            "relevance": llm_analysis.get("relevance", "unknown"),
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "status": llm_analysis.get("status", item.get("status", "new")),
            "reply": llm_analysis.get("reply", item.get("reply", ""))
        }
        
    elif source_type == "website":
        payload = {
            "client_name": item.get("client_name", "SolarisProAi"),
            "url": item.get("url", ""),
            "title": item.get("title", "No Title"),
            "content": item.get("content", "No content provided"),
            "short_description": llm_analysis.get("short_description", "No description provided"),
            "actionable": True,
            "opportunity_type": llm_analysis.get("opportunity_type", "unknown"),
            "suggested_action": llm_analysis.get("suggested_action", "No specific action suggested"),
            "relevance": llm_analysis.get("relevance", "unknown"),
            "read": False,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
    
    

    if payload:
        # Check for empty required fields based on source_type
        required_fields = []
        if source_type == "email":
            required_fields = ["content", "client_name", "type", "message_id", "subject", "processed_at", "actionable", "suggested_action", "short_description", "relevance"]
        elif source_type == "tweet":
            required_fields = ["url", "text", "actionable", "relevance", "suggested_action", "short_description", "client_name", "status", "reply"]
        elif source_type == "website":
            required_fields = ["content", "client_name", "url", "title", "short_description", "actionable", "opportunity_type", "suggested_action", "relevance", "read", "scraped_at"]

        for field in required_fields:
            if field not in payload or payload.get(field) is None:
                print(f"  -> Avertisment: Campul obligatoriu '{field}' este gol pentru {source_type}.")
                return {}, source_type # Return empty payload if a required field is empty

    return payload, source_type