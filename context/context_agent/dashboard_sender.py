import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

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
        print(f"?? Payload-ul pentru '{source_type}' a fost salvat in {output_file}")

    except IOError as e:
        print(f"?? Eroare la salvarea payload-ului in fisier: {e}")

    if source_type not in CONFIG_MAPPING:
        print(f"?? Eroare: Tipul de sursa '{source_type}' nu este valid.")
        return

    config = CONFIG_MAPPING[source_type]
    api_endpoint = config["url"]
    api_key = config["api_key"]

    if not api_endpoint or not api_key:
        print(f"?? Eroare: URL-ul sau cheia API pentru '{source_type}' nu sunt setate in .env.")
        return

    headers = {
        "X-API-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        print(f"\n?? Payload trimis la dashboard ({source_type}):\n{json.dumps(data, indent=2)}\n")
        response = requests.post(api_endpoint, json=data, headers=headers)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        print(f"📡 Response Body: {response.text}")
        response.raise_for_status()
        print(f"?? Datele trimise cu succes la dashboard ({source_type}).")
    except requests.exceptions.RequestException as e:
        print(f"?? Eroare la trimiterea datelor la dashboard ({source_type}): {e}")