# Fluxul de Procesare Individuală - Agentul `context`

Acest document descrie fluxul de procesare individuală a datelor de către agentul `context`, așa cum este orchestrat de `main_individual.py`.

Fluxul este liniar și se desfășoară în 3 etape principale: **Preluarea Datelor**, **Procesarea Individuală cu LLM** și **Trimiterea Rezultatelor**. Fiecare item (email, tweet, etc.) este tratat independent de la început până la sfârșit.

---

### 1. Preluarea și Pregătirea Datelor (`main_individual.py`)

-   **Sursa Datelor:** Procesul nu pornește de la fișiere locale statice, ci încarcă datele direct din **Supabase** folosind funcția `load_json_from_supabase`. Se încarcă:
    -   Configurația utilizatorului (`user_config`).
    -   Diverse liste de iteme: `positive_scenarios`, `neutral_scenarios`, `negative_scenarios` și `twitter_scraped`.
-   **Centralizare:** Toate aceste iteme din diverse surse sunt adunate într-o singură listă, `all_items`.
-   **Normalizare:** Scriptul parcurge rapid lista și standardizează formatul itemelor, asigurându-se că fiecare are un atribut `type` ('email', 'twitter' sau 'website').

---

### 2. Procesarea Individuală a Fiecărui Item (`main_individual.py` și `llm_context_agent_individual.py`)

Aceasta este etapa centrală, unde fiecare item este analizat pe rând, într-o buclă.

-   **Pentru fiecare item din `all_items`:**
    1.  **Context RAG:** Se extrage conținutul relevant al itemului (corpul email-ului, textul tweet-ului etc.) și se trimite la funcția `get_rag_context`. Aceasta returnează un context adițional bazat pe interacțiunile trecute, pentru a oferi o analiză mai precisă.
    2.  **Analiza LLM:** Itemul curent, împreună cu profilul utilizatorului și contextul RAG, este trimis la funcția `get_llm_analysis_individual`.
        -   În `llm_context_agent_individual.py`, se construiește un prompt foarte detaliat care instruiește modelul AI (Azure OpenAI) cum să analizeze itemul.
        -   AI-ul returnează o analiză structurată în format JSON, care conține: o descriere scurtă, dacă itemul este `actionable` (necesită o acțiune), un `priority_level` ("high", "medium", "low", "neutral"), o acțiune sugerată (`suggested_action`), și un draft de răspuns (`suggested_reply`).
    3.  **Validare:** Răspunsul JSON de la AI este validat riguros pentru a se asigura că respectă formatul așteptat. Dacă analiza eșuează, itemul este marcat automat ca "neutral".
    4.  **Colectarea Rezultatelor:** Rezultatul analizei pentru fiecare item este adăugat la o listă numită `processed_items_analysis`.

---

### 3. Salvarea și Trimiterea Datelor Procesate (`main_individual.py`, `payload_builder.py`, `dashboard_sender.py`)

După ce bucla de procesare s-a încheiat și toate itemele au fost analizate:

1.  **Salvare Locală:** Lista completă `processed_items_analysis` este salvată în fișierul `context/processed_results_individual.json`. Acesta servește ca o copie de siguranță și pentru debugging.
2.  **Formatare și Trimitere:** Scriptul parcurge noua listă de iteme analizate și, pentru fiecare:
    -   **Construiește Payload-ul:** Folosește `build_dashboard_payload` pentru a formata datele într-un "payload" specific pentru destinația finală. De exemplu, structura datelor pentru un email este diferită de cea pentru un tweet.
    -   **Trimite la Dashboard:** Folosește `send_context_to_dashboard` pentru a trimite acest payload, printr-un request API, către agentul corespunzător (de email, twitter sau website). De asemenea, o copie a payload-ului trimis este adăugată în fișierul `context/api_payloads.json` ca jurnal.
    -   **Actualizează RAG:** Dacă un item a fost marcat ca `actionable`, conținutul său este trimis înapoi către baza de date RAG. Astfel, interacțiunea curentă devine context pentru analizele viitoare.

---

Acest flux asigură că fiecare item este îmbogățit cu context, analizat individual de AI, iar rezultatul este trimis în mod structurat către sistemul central, actualizând în același timp baza de cunoștințe pentru viitor.
