from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_article(title, content):
    prompt = f"""
You are an AI assistant that analyzes business articles and extracts insights.
Given the article below, respond with a JSON object containing:

- summary (2-3 sentence summary of the article)
- label ("Actionable" or "Informational")
- opportunity_type (e.g., "New business opportunity", "Upsell context", "Partnership potential", "Networking opportunity", etc.)
- suggested_action (e.g., "Contact client", "Send proposal", "Schedule meeting", "None")

Title: {title}

Content:
{content}

Respond ONLY with a JSON object.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        reply = response.choices[0].message.content.strip()

        # Încearcă să parsezi răspunsul ca JSON
        result = json.loads(reply)

        return (
            result.get("summary", ""),
            result.get("label", ""),
            result.get("opportunity_type", ""),
            result.get("suggested_action", "")
        )

    except Exception as e:
        print(f"❌ Eroare în analiza semantică: {e}")
        return "", "", "", ""

