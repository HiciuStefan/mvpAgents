from .llm_context_agent_individual import get_llm_analysis_individual
from .rag_retriever import get_rag_context
import json
import os

def load_json_file(file_path: str) -> list:
    """
    Incarca un fisier JSON si returneaza continutul.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fisierul nu a fost gasit la calea: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Eroare la decodarea JSON din fisierul: {file_path}")
        return []

if __name__ == "__main__":
    print("Initializare procesare individuala...")

    # 1. Incarcare contexte si scenarii
    user_context = load_json_file('context/digital_excellence.json')
    output_path = 'context/processed_results.json'

    # Incarcam rezultatele procesate de batch
    if os.path.exists(output_path):
        processed_results = load_json_file(output_path)
    else:
        print(f"Fisierul {output_path} nu a fost gasit. Ruleaza mai intai procesarea batch.")
        exit()

    if not user_context or not processed_results:
        print("Oprire proces. Nu s-au putut incarca fisierele de context sau rezultatele procesate.")
        exit()

    # 2. Procesare individuala
    for result_item in processed_results:
        content = result_item.get("content")
        if not content:
            continue

        print(f"Se proceseaza individual item-ul: {content[:100]}...")

        # Obtinem context RAG specific pentru acest item
        rag_context = get_rag_context(content)

        # Apelam LLM-ul pentru analiza individuala
        llm_analysis = get_llm_analysis_individual(user_context, rag_context, {"content": content})

        # Adaugam rezultatul individual la item-ul existent
        result_item['llm_output_individual'] = llm_analysis if llm_analysis else None

    # 3. Salvare rezultate actualizate
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcesare individuala completa. Rezultatele au fost actualizate in {output_path}")
