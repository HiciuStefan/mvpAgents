from scrape_tweets import scrape_new_tweets

# Simulăm că tweeturile cu id-ul '001' și '003' au fost deja procesate
processed = {"001", "003"}

new_tweets = scrape_new_tweets(processed)

print("Tweeturi noi găsite:")
for t in new_tweets:
    print(f"- ({t['id']}) {t['text']} [from {t['url']}]")
