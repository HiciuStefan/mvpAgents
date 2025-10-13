import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
RAG_URL_POST_DELETE =  os.getenv("RAG_URL_POST_DELETE")  
RAG_URL_GET =  os.getenv("RAG_URL_GET") 
EMAIL_AGENT_API_KEY = os.getenv("EMAIL_AGENT_API_KEY")

headers = {
    "Content-Type": "application/json",
    "X-API-key": EMAIL_AGENT_API_KEY
}

def insert_base_context(context_file: str):
    """Read a JSON file and insert each context object into the database."""
    try:
        if RAG_URL_POST_DELETE is None:
                    raise ValueError("RAG_URL_POST_DELETE environment variable is not set.")
        
        with open(context_file, 'r') as file:
            data = json.load(file)
            context_list = data.get("context", [])

            for item in context_list:   
                # Insert into RAG
                payload = {
                    "input": item.get("body", "")
                }
                response = requests.post(RAG_URL_POST_DELETE, json=payload, headers=headers, timeout=10)
                response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
                print(f"✅ Sent {item.get("subject", "")},Response: {response.status_code}")

    except FileNotFoundError:
        print(f"⚠️ Context file '{context_file}' not found.")
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse JSON in '{context_file}'.")
    except Exception as err:
        print(f"⚠️ Unexpected error during delete: {err}")

def delete_base_context():
    try:
        if RAG_URL_POST_DELETE is None:
            raise ValueError("RAG_URL_POST_DELETE environment variable is not set.")
        confirmation ={
                        "confirm" : True
                }
        response = requests.delete(RAG_URL_POST_DELETE, json=confirmation, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        print(f"✅ Rag deletion response: {response.status_code}")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error during delete: {http_err}")
    except requests.exceptions.Timeout:
        print(f"⌛ Timeout during delete")
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection error during delete")
    except Exception as err:
        print(f"⚠️ Unexpected error during delete: {err}")
        
def get_relevant_context_from_rag(scenario_name: str,type: str)->str:
    """Run a specific scenario by sending a POST request to the RAG URL."""
    try:
        if RAG_URL_GET is None:
            raise ValueError("RAG_URL_GET environment variable is not set.")
        
        with open(scenario_name, 'r') as file:
            data = json.load(file)
            scenario=data.get(type, {})
            payload = {
                    "text": scenario.get("body", "")
                }
        response = requests.get(RAG_URL_GET, params=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        response_data = response.json()
        print (f"✅ RAG Retrieved response: {response.json()}")
        documents = response_data.get("data", {}).get("documents", [])

        for i, doc in enumerate(documents, start=1):
            content = doc.get("content", "")
            print(f"{i}. {content}")

        context_list = [doc.get("content", "") for doc in documents]
        print (f"✅ RAG Context list: {context_list}")
        return "\n".join(context_list)
        return json.dumps(response.json())
    
    except FileNotFoundError:
        return f"⚠️ Scenario file '{scenario_name}' not found."
    except json.JSONDecodeError:
        return f"⚠️ Failed to parse JSON in '{scenario_name}'."
    except requests.exceptions.HTTPError as http_err:
        return f"❌ HTTP error during scenario execution: {http_err}"
    except requests.exceptions.Timeout:
        return "⌛ Timeout during scenario execution"
    except requests.exceptions.ConnectionError:
        return "🚫 Connection error during scenario execution"
    except Exception as err:
        return f"⚠️ Unexpected error during scenario execution: {err}"
    