from .llm_context_agent import get_llm_analysis
from .dashboard_sender import send_context_to_dashboard
from .rag_retriever import get_rag_context
from .rag_sender import send_to_rag
from datetime import datetime, timezone
import json
import uuid

def load_json_file(file_path: str) -> list:
    """
    Incarca un fisier JSON si returneaza continutul.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fisierul nu a fost gasit la calea: {file_path}")
        return [] # Return empty list on error
    except json.JSONDecodeError:
        print(f"Eroare la decodarea JSON din fisierul: {file_path}")
        return [] # Return empty list on error

from .payload_builder import build_dashboard_payload

if __name__ == "__main__":
    print("Initializare procesare batch...")

    # 1. Incarcare contexte si scenarii
    user_context = load_json_file('context/digital_excellence.json')
    
    scenarios_to_load = {
        "positive": "context/scenarios/positive_scenarios.json",
        "neutral": "context/scenarios/neutral_scenarios.json",
        "negative": "context/scenarios/negative_scenarios.json"
    }

    all_items = []
    for scenario_type, path in scenarios_to_load.items():
        scenarios = load_json_file(path)
        for item in scenarios:
            # Add scenario type to each item
            item['scenario_type'] = scenario_type
            all_items.append(item)

    if not user_context or not all_items:
        print("Oprire proces. Nu s-au putut incarca fisierele de context sau scenariile.")
        exit()

    # 2. Normalizare si pregatire continut pentru RAG
    rag_query_content = []
    for item in all_items:
        # Normalize item structure for items coming from different sources
        if "new_email" in item:
            email_item = item.pop("new_email")
            item.update(email_item)
            item['type'] = 'email'
        
        if 'type' not in item:
            if 'subject' in item and 'body' in item:
                item['type'] = 'email'
            elif 'user' in item and 'text' in item:
                item['type'] = 'twitter'
            elif 'title' in item and 'url' in item:
                item['type'] = 'website'
            else:
                print(f"Avertisment: Item fara 'type' gasit si nu a putut fi inferat: {item}")
                continue
        
        content_for_rag = item.get('body') or item.get('content') or item.get('text')
        if content_for_rag:
            rag_query_content.append(content_for_rag)

    rag_query = " ".join(rag_query_content)
    print(f"Se genereaza contextul RAG pentru {len(all_items)} iteme...")
    rag_context = get_rag_context(rag_query)

    # 3. Apel unic catre LLM
    print("Se trimite intregul batch catre LLM pentru analiza si filtrare...")
    actionable_items_analysis = get_llm_analysis(user_context, rag_context, all_items)

    # Create a lookup for actionable items
    actionable_lookup = {}
    if actionable_items_analysis:
        for analysis in actionable_items_analysis:
            original_item = analysis.get("original_item")
            if original_item:
                # Use a tuple of identifiable fields as a key
                key = (original_item.get('type'), original_item.get('body') or original_item.get('content') or original_item.get('text'))
                actionable_lookup[key] = analysis

    # 4. Generare rezultate finale
    full_results = []
    for item in all_items:
        key = (item.get('type'), item.get('body') or item.get('content') or item.get('text'))
        analysis = actionable_lookup.get(key)

        result_item = {
            "scenario_type": item.get("scenario_type"),
            "input_type": item.get("type"),
            "content": key[1],
            "actionable": bool(analysis),
            "llm_output_batch": analysis if analysis else None
        }
        full_results.append(result_item)

    # 5. Salvare rezultate in fisier
    output_path = 'context/processed_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    print(f"\nProcesare completa. Rezultatele au fost salvate in {output_path}")

    # 6. Procesare iteme actionabile (logica existenta)
    if actionable_items_analysis:
        print(f"LLM a identificat {len(actionable_items_analysis)} iteme actionabile. Se proceseaza...")
        for analysis in actionable_items_analysis:
            original_item = analysis.get("original_item")
            if not original_item:
                print("⚠️ Avertisment: O analiza de la LLM nu contine itemul original. Se ignora.")
                continue

            payload, source_type = build_dashboard_payload(original_item, analysis)
            if payload:
                desc = analysis.get('analysis', {}).get('short_description', 'N/A')
                print(f"  -> Se trimite '{source_type}' la dashboard: {desc}")
                send_context_to_dashboard(payload, source_type)
            else:
                print(f"  -> Eroare: Nu s-a putut construi payload-ul pentru item.")

            print(f"  -> Se indexeaza '{source_type}' in RAG pentru context viitor.")
            content_to_rag = original_item.get('body') or original_item.get('content') or original_item.get('text')
            if content_to_rag:
                send_to_rag({"input": content_to_rag})
            else:
                print(f"  -> Avertisment: Nu s-a gasit continut pentru indexare RAG: {original_item}")
    else:
        print("LLM nu a identificat niciun item actionabil.")

    print("Procesare batch finalizata cu succes!")
