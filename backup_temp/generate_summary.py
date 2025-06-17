# generate_summary.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    temperature=0.5,
    model="gpt-4",
    openai_api_key=api_key
)

def generate_summary(tweet_texts: list[str]) -> str:
    """
    Primește o listă de texte (tweeturi) și returnează o sinteză scurtă.
    """
    if not tweet_texts:
        return "Nu au fost detectate tweeturi relevante."

    joined = "\n".join(f"- {t}" for t in tweet_texts)

    prompt = f"""You are a helpful assistant that summarizes the key themes of recent tweets.
Below is a list of tweets. Write a short, 1-2 sentence summary of what they are generally about.

Tweets:
{joined}

Summary:"""

    try:
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"(Eroare la generare sumar: {e})"
