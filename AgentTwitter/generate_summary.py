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

def generate_summary(tweet_text: str) -> str:
    """
    Primește un tweet și returnează un sumar scurt de 5-6 cuvinte.
    """
    prompt = f"""Summarize the following tweet in 5-6 words maximum.
Tweet: "{tweet_text}"
Summary:"""

    try:
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"(Error: {e})"

