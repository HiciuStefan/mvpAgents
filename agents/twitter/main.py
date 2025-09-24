from .scrape_tweets import scrape_new_tweets
from .state_manager import get_processed_ids, save_new_tweets
from urllib.parse import urlparse
from .classify_tweet import classify_tweet
from .send_tweets_to_api import send_tweet_to_api
from agents._tools.llm_twitterAgent import generate_summary



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
        classification = classify_tweet(tweet["text"])
        tweet["actionable"] = classification["actionable"]
        tweet["relevance"] = classification["relevance"]
        tweet["suggested_action"] = classification["suggested_action"]

        tweet["short_description"] = generate_summary(tweet["text"])
        tweet["status"] = "new"
        tweet["reply"] = ""
        # tweet["tweet_id"] = tweet.pop("id")
        account = extract_account_from_url(tweet["url"])
        tweet["account"] = account # Add account to the tweet object
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
    # save_new_tweets(all_tweets_flat)
    # print("✅ Tweeturile noi au fost salvate în tweets.json.")

    for tweet in all_tweets_flat:
        send_tweet_to_api(tweet)

    return grouped

if __name__ == "__main__":
    main()
