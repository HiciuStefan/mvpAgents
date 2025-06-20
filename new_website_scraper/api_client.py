import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv("WEBSITE_AGENT_URL")
API_KEY = os.getenv("WEBSITE_AGENT_API_KEY")


def send_article_to_api(article: dict):
    headers = {
        "X-API-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_ENDPOINT, json=article, headers=headers)
        response.raise_for_status()
        print("✅ Articol trimis cu succes la API.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Eroare la trimiterea articolului la API: {e}")
