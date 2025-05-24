from urls_data import MONITORED_URLS
from scrape_tweets import scrape_new_tweets
from generate_summary import generate_summary  # nou
from state_manager import get_processed_ids, save_new_tweets
from urllib.parse import urlparse

def extract_account_from_url(url: str) -> str:
    return urlparse(url).path.strip("/").split("/")[0]

def main():
    print("🔁 Rulăm smart_tweet_responder...")

    processed_ids = get_processed_ids()
    all_new_tweets = scrape_new_tweets(processed_ids)

    if not all_new_tweets:
        print("✅ Nu există tweeturi noi.")
        return {}

    grouped = {}
    for tweet in all_new_tweets:
        account = extract_account_from_url(tweet["url"])
        tweet["status"] = "pending"
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

# Test local
if __name__ == "__main__":
    main()
