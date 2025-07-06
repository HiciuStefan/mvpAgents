from agents.twitter.scrape_tweets import scrape_new_tweets
from urllib.parse import urlparse
from agents._tools.llm_twitterAgent import classify_tweet
from agents.common.api_sender import ApiClient
from agents._tools.llm_twitterAgent import generate_summary


def extract_account_from_url(url: str) -> str:
    return urlparse(url).path.strip("/").split("/")[0]

def main():
    print("Rulam smart_tweet_responder...")

    # Inițializează clientul API
    twitter_api_client = ApiClient(
        api_endpoint_env="TWITTER_AGENT_URL",
        api_key_env="TWITTER_AGENT_API_KEY"
    )

    all_new_tweets = scrape_new_tweets([])

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
        print(f"Pe contul @{account} am gasit {len(data['tweets'])} tweeturi noi.")
        print(f"Sumar AI: {summary}")

    # Aplatizează lista de tweet-uri pentru a le trimite
    all_tweets_flat = [t for acc in grouped.values() for t in acc["tweets"]]

    # Folosește noul ApiClient pentru a trimite tweet-urile
    print(f"Se încearcă trimiterea a {len(all_tweets_flat)} tweet-uri către API...")
    successful_sends = 0
    for tweet in all_tweets_flat:
        if twitter_api_client.send_data(tweet):
            successful_sends += 1
    
    print(f"Rezumat trimitere: {successful_sends} din {len(all_tweets_flat)} tweet-uri au fost trimise cu succes.")

    return grouped

if __name__ == "__main__":
    main()
