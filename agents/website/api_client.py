import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_ENDPOINT = os.getenv("WEBSITE_AGENT_URL")
API_KEY = os.getenv("WEBSITE_AGENT_API_KEY")


def send_article_to_api(article: dict, retries: int = 3, delay: int = 2) -> bool:
    headers = {
        "X-API-key": API_KEY,
        "Content-Type": "application/json"
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(API_ENDPOINT, json=article, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"✅ Articol trimis cu succes (încercarea {attempt})")
                return True
            else:
                print(f"⚠️ API a răspuns cu status {response.status_code} (încercarea {attempt})")
                print("🔎 Răspuns API:", response.text)

        except requests.RequestException as e:
            print(f"❌ Eroare la trimiterea articolului (încercarea {attempt}): {e}")

        # Așteaptă înainte de următoarea încercare
        if attempt < retries:
            time.sleep(delay)

    print("⛔ Toate încercările de trimitere au eșuat.")
    return False



