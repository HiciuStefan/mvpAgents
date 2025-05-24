# generate_summary.py

from llm_client import llm

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

