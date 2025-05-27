from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    temperature=0.3,
    model="gpt-4",
    openai_api_key=api_key
)

def classify_tweet(tweet_text: str) -> str:

    prompt = f"""
    You are an AI assistant that analyzes tweets to determine their business relevance.

    Your task is to classify each tweet into one of the following two categories:
    - Important: if the tweet refers to topics that could be relevant for a business (e.g. mentions of business opportunities, public recognition, customer feedback, important opinions, leadership updates, product announcements, market shifts, events etc.)
    - Neutral: if the tweet is generic, personal, unrelated to business, or not actionable

    Classify the following tweet accordingly.

    Tweet: "{tweet_text}"

    Reply only with one word: Important or Neutral.
    """

    response = llm.invoke(prompt).content.strip().lower()
    if "important" in response:
        return "important"
    else:
        return "neutral"



