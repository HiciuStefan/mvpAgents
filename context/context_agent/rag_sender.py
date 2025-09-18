import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Citim URL-ul si cheia API dedicate pentru RAG din .env
RAG_API_URL = os.getenv("RAG_API_URL")
RAG_API_KEY = os.getenv("RAG_API_KEY")

def send_to_rag(data: dict):
    """
    Trimite datele analizate catre serviciul RAG pentru a fi indexate.
    """
    if not RAG_API_URL or not RAG_API_KEY:
        print("(!) RAG_API_URL sau RAG_API_KEY nu sunt setate in .env. Trimiterea la RAG a fost anulata.")
        return

    headers = {
        "X-API-key": RAG_API_KEY, # Am schimbat aici
        "Content-Type": "application/json"
    }

    try:
        # Presupunem un sub-endpoint /index pentru a trimite date
        response = requests.post(RAG_API_URL, json=data, headers=headers)
        response.raise_for_status()
        print("Datele au fost trimise cu succes la RAG.")
    except requests.exceptions.RequestException as e:
        print(f"(!) Eroare la trimiterea datelor la RAG: {e}")

if __name__ == "__main__":
    test_data = {
        "input": "Artificial intelligence in banking is revolutionizing financial services by automating tasks, enhancing fraud detection, and personalizing customer experiences."
    }
    print(">> Trimitere date de test la RAG...")
    send_to_rag(test_data)