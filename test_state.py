from state_manager import load_existing_tweets, get_processed_ids, save_new_tweets, update_tweet_status

# 🧪 Simulează salvarea unui tweet nou
test_tweet = {
    "id": "999",
    "text": "This is a test tweet",
    "reply": "This is a test reply",
    "url": "https://twitter.com/TestUser",
    "status": "pending"
}

# Adaugă tweetul
save_new_tweets([test_tweet])

# Afișează lista actualizată
print("Tweeturi salvate:")
for tweet in load_existing_tweets():
    print(f"- ({tweet['id']}) {tweet['status']}")

# Actualizează statusul la 'approved'
update_tweet_status("999", "approved")
print("\nDupă actualizare:")
for tweet in load_existing_tweets():
    print(f"- ({tweet['id']}) {tweet['status']}")
