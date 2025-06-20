from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_article(title, content):
    prompt = f"""
You are an AI assistant that analyzes business articles and extracts insights.
You must respond with a **valid JSON object**, using only double quotes for keys and string values.

Given the article below, return a JSON object with the following fields:

- short_description (string, max 6 words)
- actionable (boolean: true or false)
- opportunity_type (string, e.g. "New business opportunity")
- suggested_action (string, e.g. "Contact client", "Send proposal", "Schedule meeting", or "None")
- relevance (string, max 100 characters, only if actionable is true; else empty string)

Example JSON format:
{{
  "short_description": "AI in insurance workflows",
  "actionable": true,
  "opportunity_type": "Partnership potential",
  "suggested_action": "Schedule meeting",
  "relevance": "This article shows how their AI solution fits our client’s business model"
}}

Now analyze the following article.

Title: {title}

Content:
{content}

Respond ONLY with a valid JSON object. Do NOT include explanations, comments, or markdown.
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
            result.get("short_description", ""),
            result.get("actionable", False),
            result.get("opportunity_type", ""),
            result.get("suggested_action", ""),
            result.get("relevance", "")
        )

    except json.JSONDecodeError as e:
        print(f"❌ Eroare în analiza semantică (JSON invalid): {e}")
        print(f"🔎 Răspunsul LLM a fost:\n{reply}")
        return "", False, "", "", ""

    except Exception as e:
        print(f"❌ Eroare generală în analiza semantică: {e}")
        return "", False, "", "", ""
