import os
import requests
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

# Citim URL-ul si cheia API dedicate pentru RAG din .env
# Incarcam variabilele de mediu doar daca nu suntem in modul de testare
if os.getenv('IS_TESTING') != 'True':
    load_dotenv()

# Citim URL-ul si cheia API dedicate pentru RAG din .env
RAG_API_URL = os.getenv("RAG_API_URL")
RAG_API_KEY = os.getenv("RAG_API_KEY")

def get_rag_context(content: str) -> str:
    """
    Interogheaza serviciul RAG pentru a obtine context relevant.
    """
    if not RAG_API_URL or not RAG_API_KEY:
        safe_print("(!) RAG_API_URL sau RAG_API_KEY nu sunt setate in .env. Se returneaza context gol.")
        return ""

    headers = {
        "X-API-key": RAG_API_KEY,  # Am schimbat aici
        "Content-Type": "application/json"
    }
    params = {"text": content}

    try:
        safe_print(f"\n>> Interogare RAG (GET) cu parametrul 'text': {content.encode('utf-8')}")
        response = requests.get(RAG_API_URL, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        documents = response_data.get("data", {}).get("documents", [])
        context_list = [doc.get("content", "") for doc in documents]
        return "\n".join(context_list)
    except requests.exceptions.RequestException as e:
        safe_print(f"(!) Eroare la preluarea contextului din RAG: {e}")
        return ""

# Cod pentru testare directa
if __name__ == "__main__":
    test_query = "AI in banking"
    safe_print(f">> Rulam testul pentru rag_retriever cu interogarea: '{test_query}'")
    context = get_rag_context(test_query)
    safe_print("\n<< Contextul returnat de RAG:")
    safe_print(context)