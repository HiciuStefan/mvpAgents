# reply_helper.py

import webbrowser
import pyperclip

def launch_reply(tweet_url: str, reply_text: str) -> None:
    """
    Varianta folosită la aprobare – deschide tweetul și copiază răspunsul.
    """
    try:
        pyperclip.copy(reply_text)
        print("✅ Răspunsul a fost copiat în clipboard.")
    except Exception as e:
        print(f"⚠️ Eroare la copiere în clipboard: {e}")
    
    webbrowser.open(tweet_url)


def post_reply(tweet_url: str, reply_text: str) -> str:
    """
    Varianta pentru postare – deschide tweetul și copiază răspunsul în clipboard.
    Returnează un mesaj pentru a fi afișat în Streamlit.
    """
    try:
        pyperclip.copy(reply_text)
        webbrowser.open(tweet_url)
        return "✅ Răspunsul a fost copiat în clipboard. Deschide caseta de reply și apasă Ctrl+V."
    except Exception as e:
        return f"⚠️ Eroare la postare sau copiere în clipboard: {e}"


# Test direct (opțional)
if __name__ == "__main__":
    tweet = "https://x.com/Lica2216/status/1923667226961355122"
    reply = "Thanks for sharing this insight! 👏"
    rezultat = post_reply(tweet, reply)
    print(rezultat)