import json
import os

DATA_FILE = "data/tweets.json"

def load_existing_tweets() -> list:
    """
    Încarcă tweeturile existente din fișierul JSON.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def get_processed_ids() -> set:
    """
    Returnează setul de tweet_id-uri deja procesate (indiferent de status).
    """
    tweets = load_existing_tweets()
    return {tweet["tweet_id"] for tweet in tweets}

def save_new_tweets(new_tweets: list):
    existing = load_existing_tweets()

    def normalize(tweet):
        return (str(tweet["tweet_id"]).strip(), tweet["text"].strip())

    existing_keys = {normalize(t) for t in existing}
    unique_new = []

    for t in new_tweets:
        key = normalize(t)
        if key not in existing_keys:
            unique_new.append(t)
            existing_keys.add(key)
        else:
            print(f"⚠️ Tweet duplicat ignorat: {t['tweet_id']}")

    if not unique_new:
        print("📭 Niciun tweet nou de salvat.")
        return

    combined = existing + unique_new
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvate {len(unique_new)} tweeturi noi în `tweets.json`.")




def update_tweet_status(tweet_id: str, new_status: str):
    """
    Actualizează statusul unui tweet identificat prin ID.
    """
    tweets = load_existing_tweets()
    modified = False

    for tweet in tweets:
        if tweet["tweet_id"] == tweet_id:
            tweet["status"] = new_status
            modified = True
            break

    if modified:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        print(f"📝 Statusul tweetului {tweet_id} a fost actualizat la `{new_status}`.")
    else:
        print(f"⚠️ Tweetul cu ID-ul {tweet_id} nu a fost găsit.")


def add_reply_to_tweet(tweet_id: str, reply_text: str = None, category: str = None):
    tweets = load_existing_tweets()
    for tweet in tweets:
        if tweet["tweet_id"] == tweet_id:
            if reply_text is not None:
                tweet["reply"] = reply_text
            if category is not None:
                tweet["category"] = category
            break
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)



def update_tweet_category(tweet_id: str, new_category: str):
    tweets = load_existing_tweets()
    for tweet in tweets:
        if tweet["tweet_id"] == tweet_id:
            tweet["category"] = new_category
            break
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)


