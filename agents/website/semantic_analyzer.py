from openai import OpenAI
from openai import AzureOpenAI
import os
import json
from dotenv import load_dotenv
from agents.twitter.context_api_fetcher import get_client_context

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY  = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION           = os.getenv("API_VERSION")
DEPLOYMENT_NAME       = os.getenv("DEPLOYMENT_NAME") 

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
    raise ValueError("Missing required environment variables: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY")

assert AZURE_OPENAI_ENDPOINT is not None
assert AZURE_OPENAI_API_KEY is not None

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
)

def analyze_article(client_name, title, content, context=""):
    context = get_client_context(client_name)

    prompt = f"""
You are an AI assistant that analyzes business articles and extracts insights.
You must respond with a **valid JSON object**, using only double quotes for keys and string values.

Given the article below, return a JSON object with the following fields:

- short_description (string, max 6 words)
- actionable (boolean: true or false)
- opportunity_type (string, e.g. "New business opportunity")
- suggested_action (string, e.g. "Contact client", "Send proposal", "Schedule meeting", etc)
- relevance (string, max 100 characters, only if actionable is true; else empty string)

Example JSON format:
{{
  "short_description": "AI in insurance workflows",
  "actionable": true,
  "opportunity_type": "Partnership potential",
  "suggested_action": "Schedule meeting",
  "relevance": "This article shows how their AI solution fits our client's business model"
}}

Now analyze the following article.

Title: {title}

Content:
{content[:3000]}

Respond ONLY with a valid JSON object. Do NOT include explanations, comments, or markdown.

Additionally, consider the following context about the client:
{context}
"""

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,                   # <-- schimbat
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        reply_content = response.choices[0].message.content
        if not reply_content:
            print("❌ Eroare: Răspunsul de la LLM este gol.")
            return "", False, "", "", ""

        reply = reply_content.strip()
        result = json.loads(reply)

        if result.get("actionable", False) and not result.get("relevance"):
            print("⚠️ Warning: Article is actionable but relevance is missing.")

        return (
            result.get("short_description", ""),
            result.get("actionable", False),
            result.get("opportunity_type", ""),
            result.get("suggested_action"
                       , ""),
            result.get("relevance", "")
        )

    except json.JSONDecodeError as e:
        print(f"❌ Eroare în analiza semantică (JSON invalid): {e}")
        print(f"🔎 Răspunsul LLM a fost:\n{reply if 'reply' in locals() else 'N/A'}")
        return "", False, "", "", ""

    except Exception as e:
        print(f"❌ Eroare generală în analiza semantică: {e}")
        return "", False, "", "", ""


if __name__ == "__main__":
    # date de test
    client_name = "AcmeCorp"
    article_title = "AI platform streamlines SME lending"
    article_content = """
    Fintech startup LendX a anunțat lansarea unei platforme AI care reduce timpul de aprobare a creditelor pentru IMM-uri la sub 24 de ore...
    """

    result = analyze_article(client_name, article_title, article_content)
    print(result)
