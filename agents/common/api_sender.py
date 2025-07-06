

import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

class ApiClient:
    """
    Un client generic pentru a trimite date către un API endpoint cu reîncercări.
    """
    def __init__(self, api_endpoint_env: str, api_key_env: str):
        """
        Initializează clientul cu endpoint-ul API și cheia API din variabilele de mediu.

        Args:
            api_endpoint_env (str): Numele variabilei de mediu pentru URL-ul API.
            api_key_env (str): Numele variabilei de mediu pentru cheia API.
        """
        self.api_endpoint = os.getenv(api_endpoint_env)
        self.api_key = os.getenv(api_key_env)
        if not self.api_endpoint or not self.api_key:
            raise ValueError(f"Variabilele de mediu {api_endpoint_env} și/sau {api_key_env} nu sunt setate.")

    def send_data(self, data: dict, retries: int = 3, delay: int = 2) -> bool:
        """
        Trimite un payload JSON la API-ul configurat, cu o logică de reîncercare.

        Args:
            data (dict): Payload-ul de trimis, în format de dicționar Python.
            retries (int): Numărul maxim de încercări.
            delay (int): Timpul de așteptare (în secunde) între încercări.

        Returns:
            bool: True dacă trimiterea a avut succes, False altfel.
        """
        headers = {
                   
            "X-API-key": self.api_key,
            "Content-Type": "application/json"
        }

        item_id = data.get('tweet_id') or data.get('url') or 'N/A'

        for attempt in range(1, retries + 1):
            try:
                print(f"\nAttempting to send item {item_id} (Attempt {attempt}/{retries})...")
                print(f"Payload trimis:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")

                response = requests.post(self.api_endpoint, json=data, headers=headers, timeout=15)

                if 200 <= response.status_code < 300:
                    print(f"✅ Item {item_id} trimis cu succes (încercarea {attempt})")
                    if attempt == retries: # If it's the last attempt and successful, return True
                        return True
                elif 400 <= response.status_code < 600:
                    print(f"⚠️ API a răspuns cu status {response.status_code} (încercarea {attempt}). Eroare irecuperabilă, oprire reîncercări.")
                    print(f"Info: Răspuns API: {response.text}")
                    return False # Stop retrying for client/server errors
                else:
                    print(f"⚠️ API a răspuns cu status {response.status_code} (încercarea {attempt})")
                    print(f"Info: Răspuns API: {response.text}")

            except requests.RequestException as e:
                print(f"❌ Eroare la trimiterea item-ului {item_id} (încercarea {attempt}): {e}")

            if attempt < retries:
                print(f"Așteptare {delay} secunde înainte de reîncercare...")
                time.sleep(delay)
            else:
                print(f"Error: Toate cele {retries} încercări de trimitere pentru item-ul {item_id} au eșuat.")
                return False
        return False # Should not be reached if logic is correct, but as a fallback

