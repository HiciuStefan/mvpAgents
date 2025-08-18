import os
import json
import sys
from .llm_context_agent import get_llm_analysis
from .dashboard_sender import send_context_to_dashboard
from .rag_retriever import get_rag_context
from .rag_sender import send_to_rag
from datetime import datetime, timezone
import uuid

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

def load_json_file(file_path: str):
    """
    Incarca un fisier JSON si returneaza continutul.
    """
    if not os.path.exists(file_path):
        safe_print(f"Fisierul nu a fost gasit la calea: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        safe_print(f"Eroare la decodarea JSON din fisierul: {file_path}")
        return None # Return None on error

from .payload_builder import build_dashboard_payload

if __name__ == "__main__":
    safe_print("Initializare procesare batch...")

    # 1. Incarcare contexte si scenarii
    user_context = load_json_file('context/digital_excellence.json')
    
    scenarios_to_load = {
        "positive": "context/scenarios/positive_scenarios.json",
        "neutral": "context/scenarios/neutral_scenarios.json",
        "negative": "context/scenarios/negative_scenarios.json", 
        "twitter": "context/scenarios/twitter_scraped.json"
    }

    all_items = []
    for scenario_type, path in scenarios_to_load.items():
        scenarios = load_json_file(path)
        if scenarios:  # Only process if scenarios were loaded successfully
            for item in scenarios:
                # Add scenario type to each item
                item['scenario_type'] = scenario_type
                all_items.append(item)

    if not user_context or not all_items:
        safe_print("Oprire proces. Nu s-au putut incarca fisierele de context sau scenariile.")
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
                safe_print(f"Avertisment: Item fara 'type' gasit si nu a putut fi inferat: {item}")
                item['type'] = 'unknown' # Assign a default type instead of skipping
        
        content_for_rag = item.get('body') or item.get('content') or item.get('text')
        if content_for_rag:
            rag_query_content.append(content_for_rag)

    rag_query = " ".join(rag_query_content)
    safe_print(f"Se genereaza contextul RAG pentru {len(all_items)} iteme...")
    rag_context = get_rag_context(rag_query)

    # 3. Apel unic catre LLM
    safe_print("Se trimite intregul batch catre LLM pentru analiza si filtrare...")
    processed_items_analysis = get_llm_analysis(user_context, rag_context, all_items)

    # 4. Salvare rezultate in fisier
    output_path = 'context/processed_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_items_analysis, f, indent=2, ensure_ascii=False)
    safe_print(f"\nProcesare completa. Rezultatele au fost salvate in {output_path}")

    # 5. Procesare si trimitere iteme la dashboard si RAG
    if processed_items_analysis:
        safe_print(f"Se proceseaza {len(processed_items_analysis)} iteme pentru trimitere la dashboard si RAG...")
        for item_with_analysis in processed_items_analysis:
            original_item = item_with_analysis.get("original_item")
            analysis = item_with_analysis.get("analysis")

            if not original_item or not analysis:
                safe_print("⚠️ Avertisment: Un item din analiza LLM nu contine original_item sau analiza. Se ignora.")
                continue

            payload, source_type = build_dashboard_payload(original_item, analysis)
            if payload:
                desc = analysis.get('short_description', 'N/A')
                safe_print(f"  -> Se trimite '{source_type}' la dashboard: {desc}")
                send_context_to_dashboard(payload, source_type)
            else:
                safe_print(f"  -> Eroare: Nu s-a putut construi payload-ul pentru item.")

            # Se indexeaza in RAG doar itemele actionable
            if analysis.get('actionable', False):
                safe_print(f"  -> Se indexeaza '{source_type}' in RAG pentru context viitor.")
                content_to_rag = original_item.get('body') or original_item.get('content') or original_item.get('text')
                if content_to_rag:
                    send_to_rag({"input": content_to_rag})
                else:
                    safe_print(f"  -> Avertisment: Nu s-a gasit continut pentru indexare RAG: {original_item}")
    else:
        safe_print("Nu s-au gasit rezultate de procesat.")

    safe_print("Procesare batch finalizata cu succes!")
