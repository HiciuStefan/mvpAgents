import os
import requests
import json
import sys
from dotenv import load_dotenv

# Fix for Windows console Unicode issues
if sys.platform == "win32":
    try:
        # Set console to UTF-8 mode on Windows 10+
        os.system("chcp 65001 > nul 2>&1")
    except:
        pass

load_dotenv()

def safe_print(text, prefix="?? "):
    """
    Safely print text that may contain Unicode characters, handling potential console encoding issues.
    """
    try:
        # Attempt to print directly
        print(f"{prefix}{text}")
    except UnicodeEncodeError:
        # If it fails, encode the string for the console's encoding, replacing unsupported characters
        output_encoding = sys.stdout.encoding or 'utf-8'
        safe_text = f"{prefix}{text}".encode(output_encoding, errors='replace').decode(output_encoding)
        print(safe_text)

# Mapping-uri pentru URL-uri si chei API
CONFIG_MAPPING = {
    "email": {
        "url": os.getenv("EMAIL_AGENT_URL"),
        "api_key": os.getenv("EMAIL_AGENT_API_KEY"),
    },
    "twitter": {
        "url": os.getenv("TWITTER_AGENT_URL"),
        "api_key": os.getenv("TWITTER_AGENT_API_KEY"),
    },
    "website": {
        "url": os.getenv("WEBSITE_AGENT_URL"),
        "api_key": os.getenv("WEBSITE_AGENT_API_KEY"),
    },
}

def send_context_to_dashboard(data: dict, source_type: str):
    """
    Trimite datele analizate catre endpoint-ul corespunzator al dashboard-ului
    si salveaza payload-ul intr-un fisier local.
    """
    # Calea catre fisierul de output
    # Se salveaza in directorul parinte (context/)
    output_file = os.path.join(os.path.dirname(__file__), '..', 'api_payloads.json')

    # Salveaza payload-ul intr-un fisier local
    try:
        all_payloads = []
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                try:
                    # Incarca datele existente
                    all_payloads = json.load(f)
                    # Se asigura ca este o lista
                    if not isinstance(all_payloads, list):
                        all_payloads = []
                except json.JSONDecodeError:
                    # Daca fisierul este gol sau corupt, incepe cu o lista goala
                    all_payloads = []
        
        # Adauga noul payload la lista
        all_payloads.append({
            "source": source_type,
            "payload": data
        })

        # Scrie lista actualizata inapoi in fisier
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_payloads, f, indent=2, ensure_ascii=False)
        safe_print(f"Payload-ul pentru '{source_type}' a fost salvat in {output_file}")

    except IOError as e:
        safe_print(f"Eroare la salvarea payload-ului in fisier: {e}")

    if source_type not in CONFIG_MAPPING:
        safe_print(f"Eroare: Tipul de sursa '{source_type}' nu este valid.")
        return

    config = CONFIG_MAPPING[source_type]
    api_endpoint = config["url"]
    api_key = config["api_key"]

    if not api_endpoint or not api_key:
        safe_print(f"Eroare: URL-ul sau cheia API pentru '{source_type}' nu sunt setate in .env.")
        return

    headers = {
        "X-API-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Safely print the payload
        payload_str = json.dumps(data, indent=2, ensure_ascii=False)
        safe_print(f"\nPayload trimis la dashboard ({source_type}):\n{payload_str}\n", "")
        
        response = requests.post(api_endpoint, json=data, headers=headers)
        safe_print(f"Response Status: {response.status_code}", "")
        safe_print(f"Response Headers: {dict(response.headers)}", "")
        
        # Handle response text safely
        try:
            safe_print(f"Response Body: {response.text}", "")
        except UnicodeEncodeError:
            # Fallback: print response text with problematic characters replaced
            safe_text = response.text.encode('utf-8', errors='replace').decode('utf-8')
            safe_print(f"Response Body: {safe_text}", "")
        
        response.raise_for_status()
        safe_print(f"Datele trimise cu succes la dashboard ({source_type}).")
    except requests.exceptions.RequestException as e:
        safe_print(f"Eroare la trimiterea datelor la dashboard ({source_type}): {e}")