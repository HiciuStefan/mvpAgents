import os
import json
import sys
from datetime import datetime, timezone
import uuid
from .payload_builder import build_dashboard_payload

def safe_print(text, prefix=""):
    """
    Safely print text that may contain Unicode characters
    """
    try:
        print(f"{prefix}{text}")
    except UnicodeEncodeError:
        # Fallback: encode with replacement characters
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(f"{prefix}{safe_text}")

def test_payload_builder():
    """
    Testeaza functia build_dashboard_payload cu date de test.
    """
    # Date de test pentru un email
    test_email = {
        "type": "email",
        "subject": "Test Subject",
        "body": "Test email body content",
        "from": "test@example.com",
        "to": "recipient@example.com",
        "date": "2024-01-01T00:00:00Z"
    }

    # Analiza LLM simulata
    test_analysis = {
        "short_description": "Test email analysis",
        "actionable": True,
        "priority_level": "medium",
        "opportunity_type": "Test opportunity",
        "suggested_action": "Test action",
        "relevance": "Test relevance",
        "suggested_reply": "Test reply"
    }

    try:
        # Construieste payload-ul
        payload, source_type = build_dashboard_payload(test_email, test_analysis)
        
        if payload:
            safe_print("✅ Payload construit cu succes!")
            safe_print(f"Tip sursa: {source_type}")
            safe_print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # Valideaza campurile obligatorii
            required_fields = ['content', 'type', 'actionable']
            for field in required_fields:
                if field not in payload or payload[field] is None:
                    safe_print(f"  -> DEBUG: Validation failed. Required field '{field}' is missing or None.")
                else:
                    safe_print(f"  -> DEBUG: Field '{field}' is valid: {payload[field]}")
        else:
            safe_print("❌ Eroare: Nu s-a putut construi payload-ul.")
            
    except Exception as e:
        safe_print(f"❌ Eroare la testarea payload builder: {e}")

if __name__ == "__main__":
    test_payload_builder()