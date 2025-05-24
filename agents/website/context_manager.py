import json
import os
from collections import defaultdict

# Calea către fișierele sursă
ARTICLES_FILE = "context/processed_articles.json"
TWEETS_FILE = "context/tweets.json"
EMAILS_FILE = "context/emails.json"


def safe_load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Eroare la parsarea {file_path}. Verifică formatul JSON.")
            return []


def build_context():
    context = defaultdict(str)

    # Articole procesate
    articles = safe_load_json(ARTICLES_FILE)
    for article in articles:
        name = article.get("client_name", "").strip()
        if name:
            context[name] += f"[Article] {article.get('title', '')} — {article.get('content', '')}\n"

    # Tweets
    tweets = safe_load_json(TWEETS_FILE)
    for tweet in tweets:
        name = tweet.get("client_name", "").strip()
        if name:
            context[name] += f"[Tweet] {tweet.get('text', '')} — {tweet.get('text', '')}\n"

    # Emailuri
    emails = safe_load_json(EMAILS_FILE)
    for email in emails:
        name = email.get("client_name", "").strip()
        if name:
            context[name] += f"[Email] {email.get('subject', '')} — {email.get('content', '')}\n"

    return context


# Construim contextul o singură dată la încărcare
client_context_map = build_context()

def get_client_context(client_name: str) -> str:
    return client_context_map.get(client_name.strip(), "")
