from urls_data import MONITORED_URLS
from scrape_tweets import scrape_new_tweets
from generate_summary import generate_summary
from state_manager import get_processed_ids, save_new_tweets
from urllib.parse import urlparse
from generate_reply import generate_reply
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    temperature=0,
    model="gpt-4",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def extract_account_from_url(url: str) -> str:
    return urlparse(url).path.strip("/").split("/")[0]

def classify_tweet(tweet_text: str) -> str:
    prompt = f"""
You are an AI assistant that analyzes tweets to determine their business relevance.

Your task is to classify each tweet into one of the following two categories:
- Important: if the tweet refers to topics that could be relevant for a business (e.g. mentions of business opportunities, public recognition, customer feedback, important opinions, leadership updates, product announcements, market shifts, events etc.)
- Neutral: if the tweet is generic, personal, unrelated to business, or not actionable

Classify the following tweet accordingly.

Tweet: "{tweet_text}"

Reply only with one word: Important or Neutral.
"""
    response = llm.invoke(prompt).content.strip().lower()
    return "important" if "important" in response else "neutral"

def main():
    print("🔁 Rulăm smart_tweet_responder...")

    processed_ids = get_processed_ids()
    all_new_tweets = scrape_new_tweets(processed_ids)

    if not all_new_tweets:
        print("✅ Nu există tweeturi noi.")
        return {}

    grouped = {}
    for tweet in all_new_tweets:
        tweet["category"] = classify_tweet(tweet["text"])
        tweet["status"] = "pending"
        account = extract_account_from_url(tweet["url"])
        if account not in grouped:
            grouped[account] = {
                "url": f"https://twitter.com/{account}",
                "tweets": []
            }
        grouped[account]["tweets"].append(tweet)

    for account, data in grouped.items():
        texts = [t["text"] for t in data["tweets"]]
        summary = generate_summary(texts)
        grouped[account]["summary"] = summary
        print(f"🧵 Pe contul @{account} am găsit {len(data['tweets'])} tweeturi noi.")
        print(f"📋 Sumar AI: {summary}")

    # Salvează toate tweeturile în tweets.json
    all_tweets_flat = [t for acc in grouped.values() for t in acc["tweets"]]
    save_new_tweets(all_tweets_flat)

    return grouped

if __name__ == "__main__":
    main()
