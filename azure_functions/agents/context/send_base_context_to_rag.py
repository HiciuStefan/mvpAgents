import os
import json
import sys
from dotenv import load_dotenv
from .rag_sender import send_to_rag
from supabase_retriever import load_json_from_supabase

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

load_dotenv()

def main():
    """
    Functia principala care trimite contextul de baza catre RAG.
    """
    # Incarcam contextul de baza din Supabase
    base_context_data = load_json_from_supabase('base_context')

    if not base_context_data or 'context' not in base_context_data:
        safe_print("(!) Eroare: Nu s-a putut încărca base_context sau formatul este invalid.")
        return

    entries_to_send = []
    for item in base_context_data['context']:
        # Construct the input string from the item's content
        input_text = f"Type: {item.get('type', 'N/A')}\n"
        if 'title' in item:
            input_text += f"Title: {item.get('title', 'N/A')}\n"
        if 'content' in item:
            input_text += f"Content: {item.get('content', 'N/A')}\n"
        if 'body' in item:
            input_text += f"Body: {item.get('body', 'N/A')}\n"
        if 'recommendation' in item:
            recommendation = item.get('recommendation', {})
            input_text += f"Recommendation Action: {recommendation.get('action', 'N/A')}\n"
            input_text += f"Recommendation Reasoning: {recommendation.get('reasoning', 'N/A')}"

        entry = {
            "input": input_text,
            "metadata": {"type": item.get("type", "general"), "source": "base_context"}
        }
        entries_to_send.append(entry)

    safe_print(f"Se trimit {len(entries_to_send)} intrari din base_context catre RAG...")

    # Trimitem fiecare intrare catre RAG
    success_count = 0
    for entry in entries_to_send:
        if send_to_rag(entry):
            success_count += 1

    safe_print(f"Trimitere completa. {success_count}/{len(entries_to_send)} intrari trimise cu succes.")

if __name__ == "__main__":
    main()