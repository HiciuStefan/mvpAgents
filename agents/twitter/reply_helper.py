# reply_helper.py

import webbrowser
import pyperclip

def prepare_reply(tweet_url: str, reply_text: str) -> None:
    """
    Opens the target tweet URL in the default browser and copies the reply
    text to the clipboard.
    """
    try:
        pyperclip.copy(reply_text)
        webbrowser.open(tweet_url)
    except Exception as e:
        # In a real application, this should be handled by a logger.
        print(f"An error occurred while preparing the reply: {e}")


# Direct test (optional)
if __name__ == "__main__":
    test_tweet_url = "https://x.com/Lica2216/status/1956273442841330103"
    test_reply_text = "Thanks for sharing this insight!"
    
    print("Running test for prepare_reply...")
    prepare_reply(test_tweet_url, test_reply_text)
    print("Test finished. Check your browser and clipboard.")