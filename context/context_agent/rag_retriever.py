import os
import requests
from dotenv import load_dotenv

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
        print("(!) RAG_API_URL sau RAG_API_KEY nu sunt setate in .env. Se returneaza context gol.")
        return ""

def get_rag_context(content: str) -> str:
    """
    Interogheaza serviciul RAG pentru a obtine context relevant.
    """
    if not RAG_API_URL or not RAG_API_KEY:
        print("(!) RAG_API_URL sau RAG_API_KEY nu sunt setate in .env. Se returneaza context gol.")
        return ""

    headers = {
        "X-API-key": RAG_API_KEY,  # Am schimbat aici
        "Content-Type": "application/json"
    }
    params = {"text": content}

    try:
        print(f"\n>> Interogare RAG (GET) cu parametrul 'text': {content.encode('utf-8')}")
        response = requests.get(RAG_API_URL, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        documents = response_data.get("data", {}).get("documents", [])
        context_list = [doc.get("content", "") for doc in documents]
        return "\n".join(context_list)
    except requests.exceptions.RequestException as e:
        print(f"(!) Eroare la preluarea contextului din RAG: {e}")
        return ""

# Cod pentru testare directa
if __name__ == "__main__":
    test_query = "AI in banking"
    print(f">> Rulam testul pentru rag_retriever cu interogarea: '{test_query}'")
    context = get_rag_context(test_query)
    print("\n<< Contextul returnat de RAG:")
    print(context)