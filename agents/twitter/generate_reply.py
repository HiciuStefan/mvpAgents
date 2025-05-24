# generate_reply.py

from llm_client import llm

def generate_reply(tweet_text: str) -> str:
    """
    Generează un răspuns scurt și prietenos pentru un tweet.
    """
    prompt = f"""You are a helpful AI assistant that writes thoughtful, concise Twitter replies.
Tweet: "{tweet_text}"
Reply:"""
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"❌ Eroare la generarea răspunsului GPT: {e}")
        return "Thank you for sharing your thoughts!"

