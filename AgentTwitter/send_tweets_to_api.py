import os
import requests
import json
from dotenv import load_dotenv

# Încarcă variabilele din fișierul .env
load_dotenv()

API_ENDPOINT = os.getenv("TWITTER_API_URL")
API_KEY = os.getenv("TWITTER_API_KEY")


def send_tweet_to_api(tweet: dict):
    headers = {
        "X-API-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        print(f"\n📦 Payload trimis:\n{json.dumps(tweet, indent=2, ensure_ascii=False)}\n")
        response = requests.post(API_ENDPOINT, json=tweet, headers=headers)
        response.raise_for_status()
        print(f"✅ Tweet-ul {tweet['tweet_id']} trimis cu succes la API.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Eroare la trimiterea tweet-ului {tweet.get('tweet_id', 'N/A')} la API: {e}")


if __name__ == "__main__":
    # Încarcă tweeturile din fișier doar dacă rulezi acest fișier direct
    with open("twitter_records.json", "r", encoding="utf-8") as file:
        tweets = json.load(file)

    for tweet in tweets:
        send_tweet_to_api(tweet)
