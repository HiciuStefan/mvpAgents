import os
import requests
import json
import sys
from dotenv import load_dotenv

def safe_print(text, prefix=""):
    """
    Safely print text that may contain Unicode characters
    """
    try:
        print(f"{prefix}{text}")
    except UnicodeEncodeError:
        # Fallback: encode with replacement characters
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(f"{prefix}{safe_text}")

load_dotenv()

# Citim URL-ul si cheia API dedicate pentru RAG din .env
RAG_API_URL = os.getenv("RAG_API_URL")
RAG_API_KEY = os.getenv("RAG_API_KEY")

def send_to_rag(data: dict) -> bool:
    """
    Trimite date catre serviciul RAG pentru indexare.
    """
    if not RAG_API_URL or not RAG_API_KEY:
        safe_print("(!) RAG_API_URL sau RAG_API_KEY nu sunt setate in .env.")
        return False

    headers = {
        "X-API-key": RAG_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(RAG_API_URL, json=data, headers=headers)
        response.raise_for_status()
        safe_print("Datele au fost trimise cu succes la RAG.")
        return True
    except requests.exceptions.RequestException as e:
        safe_print(f"(!) Eroare la trimiterea datelor la RAG: {e}")
        return False

if __name__ == "__main__":
    test_data = {
        "input": "Artificial intelligence in banking is revolutionizing financial services by automating tasks, enhancing fraud detection, and personalizing customer experiences."
    }
    safe_print(">> Trimitere date de test la RAG...")
    send_to_rag(test_data)