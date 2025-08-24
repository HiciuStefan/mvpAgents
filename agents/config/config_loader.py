from typing import Any, Dict
# Presupunem că supabase_retriever este în PYTHONPATH
from supabase_retriever import load_json_from_supabase

def load_user_profile() -> Dict[str, Any]:
    """Încarcă profilul utilizatorului din Supabase (item-ul 'user_config')."""
    user_config = load_json_from_supabase('user_config')
    if user_config:
        return user_config
    # Returnează un dicționar gol dacă nu se găsește configurația pentru a evita erorile
    return {}