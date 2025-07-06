import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBSITE_URL = os.getenv("WEBSITE_AGENT_URL")
WEBSITE_KEY = os.getenv("WEBSITE_AGENT_API_KEY")
TWITTER_URL = os.getenv("TWITTER_AGENT_URL")
TWITTER_KEY = os.getenv("TWITTER_AGENT_API_KEY")

def fetch_context_from_api(base_url, api_key, client_name):
    headers = {"X-API-key": api_key}
    params = {
        "client_name": client_name,
        "limit": 3  # extrage până la 3 înregistrări
    }

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])  # ne asigurăm că extragem lista
    
    except Exception as e:
        print(f"⚠️ Eroare la preluarea contextului din {base_url}: {e}")
        return []

def get_client_context(client_name):
    website_data = fetch_context_from_api(WEBSITE_URL, WEBSITE_KEY, client_name)
    twitter_data = fetch_context_from_api(TWITTER_URL, TWITTER_KEY, client_name)

    context_parts = []

    for item in website_data:
        if isinstance(item, dict):
            content = item.get("content") or item.get("title")
            if content:
                context_parts.append(f"[Website] {content.strip()}")

    for item in twitter_data:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                context_parts.append(f"[Twitter] {text.strip()}")

    if not context_parts:
        return ""

    # ✂️ Limităm fiecare bucată și tot contextul total
    max_context_length = 6000
    max_len_per_item = 1000
    joined = ""
    for part in context_parts:
        trimmed = part[:max_len_per_item]
        if len(joined) + len(trimmed) > max_context_length:
            break
        joined += trimmed + "\n"

    return joined.strip()
