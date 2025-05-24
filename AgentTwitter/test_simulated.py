from urls_data import SIMULATED_TWEET_DATA

print("Date simulate:")
for url, tweets in SIMULATED_TWEET_DATA.items():
    print(f"\n{url}")
    for tweet in tweets:
        print(f"- ({tweet['id']}) {tweet['text']}")
