from .llm_context_agent import get_llm_analysis
from .dashboard_sender import send_context_to_dashboard
from .rag_retriever import get_rag_context
from .rag_sender import send_to_rag
from datetime import datetime, timezone
import json
import uuid

def load_json_file(file_path: str) -> dict:
    """
    Incarca un fisier JSON si returneaza continutul.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fisierul nu a fost gasit la calea: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Eroare la decodarea JSON din fisierul: {file_path}")
        return {}

from .payload_builder import build_dashboard_payload

if __name__ == "__main__":
    print("Initializare procesare batch...")

    # 1. Incarcare contexte
    user_context = load_json_file('context/digital_excellence.json')
    # Incarcare fisiere de scenarii individuale
    negative_scenarios = load_json_file('context/scenarios/negative_scenarios.json')
    neutral_scenarios = load_json_file('context/scenarios/neutral_scenarios.json')
    positive_scenarios = load_json_file('context/scenarios/positive_scenarios.json')

    # Combinare date din scenarii
    scenarios_data = {
        'emails': [],
        'tweets': [],
        'website_articles': []
    }

    for scenario_list in [negative_scenarios, neutral_scenarios, positive_scenarios]:
        for item_wrapper in scenario_list:
            if "new_email" in item_wrapper:
                # Handle the case where email is nested under "new_email"
                email_item = item_wrapper["new_email"]
                email_item['type'] = 'email' # Ensure type is set for consistency
                scenarios_data['emails'].append(email_item)
            elif "type" in item_wrapper:
                item_type = item_wrapper["type"]
                if item_type == "email":
                    scenarios_data['emails'].append(item_wrapper)
                elif item_type == "twitter":
                    scenarios_data['tweets'].append(item_wrapper)
                elif item_type == "website":
                    scenarios_data['website_articles'].append(item_wrapper)
                else:
                    print(f"Avertisment: Tip de item necunoscut gasit: {item_type}")
            else:
                print(f"Avertisment: Item fara 'type' sau 'new_email' gasit: {item_wrapper}")

    if not user_context or not scenarios_data:
        print("Oprire proces. Nu s-au putut incarca fisierele de context.")
        exit()

    # 2. Concatenare continut pentru query-ul RAG
    all_items = []
    rag_query_content = []
    for key in ['emails', 'tweets', 'website_articles']:
        items = scenarios_data.get(key, [])
        for item in items:
            # Adaugam un camp `type` pentru a sti sursa originala
            item['type'] = 'tweet' if key == 'tweets' else (key.replace('_articles', '').rstrip('s') if key != 'website_articles' else 'website') 
            all_items.append(item)
            content_for_rag = item.get('body') or item.get('content')
            if content_for_rag:
                rag_query_content.append(content_for_rag)
    
    rag_query = " ".join(rag_query_content)
    print(f"Se genereaza contextul RAG pentru {len(all_items)} iteme...")
    rag_context = get_rag_context(rag_query)

    # 3. Apel unic catre LLM cu intregul batch
    print("Se trimite intregul batch catre LLM pentru analiza si filtrare...")
    actionable_items_analysis = get_llm_analysis(user_context, rag_context, all_items)

    if not actionable_items_analysis:
        print("Procesare finalizata. LLM nu a identificat niciun item actionabil.")
        exit()

    print(f"LLM a identificat {len(actionable_items_analysis)} iteme actionabile. Se proceseaza...")

    # 4. Procesare iteme actionabile
    for analysis in actionable_items_analysis:
        original_item = analysis.get("original_item")
        if not original_item:
            print("⚠️ Avertisment: O analiza de la LLM nu contine itemul original. Se ignora.")
            continue

        # a. Construire payload si trimitere la dashboard
        payload, source_type = build_dashboard_payload(original_item, analysis)
        if payload:
            print(f"  -> Se trimite '{source_type}' la dashboard: {analysis['analysis']['short_description']}")
            send_context_to_dashboard(payload, source_type)
        else:
            print(f"  -> Eroare: Nu s-a putut construi payload-ul pentru item.")

        # b. Trimitere la RAG pentru indexare
        print(f"  -> Se indexeaza '{source_type}' in RAG pentru context viitor.")
        content_to_rag = original_item.get('body') or original_item.get('content')
        if content_to_rag:
            send_to_rag({"input": content_to_rag})
        else:
            print(f"  -> Avertisment: Nu s-a gasit 'body' sau 'content' pentru indexare RAG: {original_item}")

    print("Procesare batch finalizata cu succes!")
