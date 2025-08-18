
import os
import json
import sys
from dotenv import load_dotenv
from .rag_sender import send_to_rag

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

# Calea catre fisierul de context de baza
BASE_CONTEXT_PATH = 'context/digital_excellence.json'

def main():
    """
    Functia principala care trimite contextul de baza catre RAG.
    """
    # Verificam daca fisierul de context de baza exista
    if not os.path.exists(BASE_CONTEXT_PATH):
        safe_print(f"(!) Eroare: Fisierul {BASE_CONTEXT_PATH} nu a fost gasit.")
        return

    try:
        # Incarcam contextul de baza
        with open(BASE_CONTEXT_PATH, 'r', encoding='utf-8') as f:
            base_context = json.load(f)
    except json.JSONDecodeError:
        safe_print(f"(!) Eroare: Fisierul {BASE_CONTEXT_PATH} nu este un JSON valid.")
        return

    # Extragem intrari specifice pentru SolarisProAi
    solaris_pro_ai_entries = []
    
    # Adaugam informatii despre companie
    company_info = {
        "input": f"Company: {base_context.get('company', 'N/A')} - {base_context.get('tagline', 'N/A')}",
        "metadata": {"type": "company_info", "source": "digital_excellence.json"}
    }
    solaris_pro_ai_entries.append(company_info)
    
    # Adaugam misiunea si viziunea
    mission_vision = {
        "input": f"Mission: {base_context.get('mission', 'N/A')} Vision: {base_context.get('vision', 'N/A')}",
        "metadata": {"type": "mission_vision", "source": "digital_excellence.json"}
    }
    solaris_pro_ai_entries.append(mission_vision)
    
    # Adaugam serviciile
    services = base_context.get('services', [])
    if services:
        services_text = "Services: " + "; ".join(services)
        services_entry = {
            "input": services_text,
            "metadata": {"type": "services", "source": "digital_excellence.json"}
        }
        solaris_pro_ai_entries.append(services_entry)

    safe_print(f"Se trimit {len(solaris_pro_ai_entries)} intrari SolarisProAi catre RAG...")
    
    # Trimitem fiecare intrare catre RAG
    success_count = 0
    for entry in solaris_pro_ai_entries:
        if send_to_rag(entry):
            success_count += 1
    
    safe_print(f"Trimitere completa. {success_count}/{len(solaris_pro_ai_entries)} intrari trimise cu succes.")

if __name__ == "__main__":
    main()
