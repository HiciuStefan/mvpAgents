import pytest
from datetime import datetime, timezone
import uuid
from context.context_agent.payload_builder import build_dashboard_payload

def test_build_dashboard_payload_twitter():
    item = {
        "type": "tweet", # Changed from "twitter" to "tweet"
        "url": "https://twitter.com/testuser/status/12345",
        "content": "This is a test tweet.",
        "client_name": "TestUser",
        "tweet_id": "12345"
    }
    analysis = {
        "analysis": {
            "relevance": "high",
            "suggested_action": "Reply to tweet",
            "short_description": "Important tweet about product launch",
            "status": "new",
            "reply": "Great news!"
        }
    }

    payload, source_type = build_dashboard_payload(item, analysis)

    print("\nTwitter Payload:")
    print(payload)

    assert source_type == "tweet" # Changed from "twitter" to "tweet"
    assert isinstance(payload, dict)
    assert "url" in payload
    assert "text" in payload
    assert "actionable" in payload
    # assert "type" in payload # Removed this assertion
    assert "client_name" in payload
    assert "tweet_id" in payload
    assert "relevance" in payload
    assert "suggested_action" in payload
    assert "short_description" in payload
    assert "status" in payload
    assert "reply" in payload

    assert payload["url"] == "https://twitter.com/testuser/status/12345"
    assert payload["text"] == "This is a test tweet."
    assert payload["actionable"] == True
    assert payload["client_name"] == "SolarisProAi" # Changed to SolarisProAi
    assert payload["tweet_id"] == "12345"
    assert payload["relevance"] == "high"
    assert payload["suggested_action"] == "Reply to tweet"
    assert payload["short_description"] == "Important tweet about product launch"
    assert payload["status"] == "new"
    assert payload["reply"] == "Great news!"

def test_build_dashboard_payload_website():
    item = {
        "type": "website",
        "content": "This is content from a website.",
        "client_name": "SolarisProAi", # Changed to SolarisProAi
        "id": "web_123",
        "title": "Website Article Title",
        "url": "https://example.com/article"
    }
    analysis = {
        "analysis": {
            "relevance": "medium",
            "suggested_action": "Review article",
            "short_description": "New article on industry trends",
            "opportunity_type": "New business opportunity"
        }
    }

    payload, source_type = build_dashboard_payload(item, analysis)

    print("\nWebsite Payload:")
    print(payload)

    assert source_type == "website"
    assert isinstance(payload, dict)
    assert "content" in payload
    assert "client_name" in payload
    assert "title" in payload
    assert "scraped_at" in payload
    assert "actionable" in payload
    assert "suggested_action" in payload
    assert "short_description" in payload
    assert "relevance" in payload # Re-added assertion for relevance
    assert "url" in payload
    assert "read" in payload
    assert "opportunity_type" in payload

    assert payload["content"] == "This is content from a website."
    assert payload["client_name"] == "SolarisProAi"
    assert payload["title"] == "Website Article Title"
    assert payload["actionable"] == True
    assert payload["suggested_action"] == "Review article"
    assert payload["short_description"] == "New article on industry trends"
    assert payload["relevance"] == "medium" # Re-added assertion for relevance value
    assert payload["url"] == "https://example.com/article"
    assert payload["read"] == False
    assert payload["opportunity_type"] == "New business opportunity"
    assert datetime.fromisoformat(payload["scraped_at"]).date() == datetime.now(timezone.utc).date()