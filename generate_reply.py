# generate_reply.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Inițializează modelul LLM
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4",
    openai_api_key=api_key
)

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

