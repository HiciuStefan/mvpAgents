from typing import Dict, Any


def build_twitter_payload(tweet: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construieste payload-ul pentru endpoint-ul de Twitter al dashboard-ului.
    - Include atat campurile cerute de backend (status, reply),
      cat si campurile folosite in context_agent (suggested_reply, urgency).
    """

    actionable = bool(classification.get("actionable", False))

    short_description = classification.get("short_description")
    if not short_description or short_description.strip() == "":
        # Fallback: taie textul tweet-ului daca lipseste
        text_for_desc = tweet.get("text", "No content provided")
        short_description = (text_for_desc[:47] + "...") if len(text_for_desc) > 50 else text_for_desc

    suggested_action = classification.get("suggested_action")
    if actionable and (not suggested_action or suggested_action.strip() == ""):
        suggested_action = "Review and determine next steps."
    if not actionable:
        suggested_action = " "

    relevance = classification.get("relevance")
    if actionable and (not relevance or relevance.strip() == ""):
        relevance = "Importance requires further review."
    if not actionable:
        relevance = " "

    # Mapare priority_level -> urgency (ca in context_agent)
    priority_level = classification.get("priority_level") or ("neutral" if not actionable else "low")
    priority_mapping = {"neutral": 0, "low": 1, "medium": 2, "high": 3}
    urgency = priority_mapping.get(priority_level, 0)

    suggested_reply = classification.get("suggested_reply")
    if actionable and (not suggested_reply or suggested_reply.strip() == ""):
        suggested_reply = "Thank you for the update!"
    if not actionable:
        suggested_reply = " "

    payload = {
        # Campuri comune si cerute de backend
        "client_name": tweet.get("client_name") or "SolarisProAi",
        "short_description": short_description[:50],
        "relevance": relevance,
        "actionable": actionable,
        "suggested_action": suggested_action,
        "tweet_id": tweet.get("tweet_id", "000000000"),
        "url": tweet.get("url", "https://twitter.com/unknown/status/00000"),
        "text": tweet.get("text", "No content provided"),
        # Campuri suplimentare folosite in context_agent
        "suggested_reply": suggested_reply,
        "urgency": urgency,
    }

    return payload


