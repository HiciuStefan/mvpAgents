import os
import json
import sys
from .llm_context_agent_individual import get_llm_analysis_individual
from .rag_retriever import get_rag_context

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
        return None

if __name__ == "__main__":
    # Calea catre fisierul cu rezultatele procesate
    output_path = 'context/processed_results.json'
    
    # Verificam daca fisierul cu rezultate exista
    if not os.path.exists(output_path):
        safe_print(f"Fisierul {output_path} nu a fost gasit. Ruleaza mai intai procesarea batch.")
        exit()
    
    # Incarcam rezultatele procesate
    processed_results = load_json_file(output_path)
    if not processed_results:
        safe_print("Nu s-au putut incarca rezultatele procesate.")
        exit()
    
    # Incarcam contextul utilizatorului
    user_context = load_json_file('context/digital_excellence.json')
    if not user_context:
        safe_print("Nu s-au putut incarca datele de context ale utilizatorului.")
        exit()
    
    # Procesam fiecare item individual
    for i, item_with_analysis in enumerate(processed_results):
        original_item = item_with_analysis.get("original_item")
        if not original_item:
            continue
            
        # Extragem continutul pentru analiza individuala
        content = original_item.get('body') or original_item.get('content') or original_item.get('text', '')
        if not content:
            continue
            
        safe_print(f"Se proceseaza individual item-ul: {content[:100]}...")
        
        # Obtinem contextul RAG
        rag_context = get_rag_context(content)
        
        # Analizam item-ul individual
        individual_analysis = get_llm_analysis_individual(user_context, rag_context, original_item)
        
        if individual_analysis:
            # Actualizam analiza in rezultatele procesate
            processed_results[i]['analysis'] = individual_analysis
            safe_print(f"✅ Analiza individuala completa pentru item-ul {i+1}")
        else:
            safe_print(f"⚠️ Nu s-a putut obtine analiza individuala pentru item-ul {i+1}")
    
    # Salvam rezultatele actualizate
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, indent=2, ensure_ascii=False)
    
    safe_print(f"\nProcesare individuala completa. Rezultatele au fost actualizate in {output_path}")
