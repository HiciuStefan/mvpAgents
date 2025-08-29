# Explicația Fișierului `simple_scraper.py`

Gândește-te la acest script ca la un **robot inteligent și eficient** pe care îl trimiți să aducă articole de pe diferite site-uri web. Spre deosebire de un robot simplu care are nevoie de instrucțiuni exacte pentru fiecare site, acesta este suficient de deștept încât să se descurce singur și, mai important, **învață din rulările anterioare pentru a nu face muncă inutilă**.

Funcționarea lui se bazează pe 3 pași principali, pe care îi execută cu ajutorul unui model de Inteligență Artificială (LLM), și pe un sistem inteligent de memorare a stării.

### Pasul 1: Găsește pagina cu articole (Blog / Știri)

*   **Problemă:** Un site are multe pagini (Acasă, Contact, Despre, etc.). Robotul trebuie să găsească pagina principală unde sunt listate toate articolele (de obicei se numește "Blog", "Știri", "Noutăți", etc.).
*   **Soluția inteligentă:**
    1.  Robotul intră pe pagina de start a site-ului (ex: `www.exemplu.ro`).
    2.  Se uită la toate link-urile de pe acea pagină.
    3.  Trimite lista de link-uri către "creierul" său (Inteligența Artificială) și întreabă: "Care dintre aceste link-uri pare a fi pagina principală de blog sau știri?".
    4.  AI-ul îi răspunde cu link-ul cel mai probabil (ex: `www.exemplu.ro/blog`). Dacă AI-ul nu găsește, scriptul încearcă o variantă de rezervă (ex: adaugă `/blog/` la adresa principală).

### Pasul 2: Identifică fiecare articol în parte

*   **Problemă:** Pagina de blog conține o listă de articole, dar și alte link-uri (către categorii, autori, paginile următoare, etc.). Robotul trebuie să ia doar link-urile care duc la un articol complet.
*   **Soluția inteligentă:**
    1.  Robotul accesează pagina de blog găsită la pasul 1.
    2.  Se uită la toate link-urile de pe această pagină.
    3.  Trimite noua listă la AI și întreabă: "Care dintre acestea sunt link-uri directe către articole individuale?".
    4.  AI-ul îi returnează o listă curată, doar cu link-urile către articole.

### Pasul 3: Extrage informațiile utile și aplică filtre de calitate

*   **Problemă:** O pagină de articol conține textul principal, dar și meniuri, reclame, subsolul paginii, etc. Robotul trebuie să extragă doar esențialul și să se asigure că informația este relevantă.
*   **Soluția inteligentă:**
    1.  Pentru fiecare link de articol nou, robotul descarcă pagina.
    2.  Face o primă curățare, eliminând elementele evidente (meniuri, subsol, etc.) folosind o unealtă numită `BeautifulSoup`.
    3.  Trimite HTML-ul curățat la AI cu instrucțiuni clare: "Analizează acest cod și extrage-mi titlul, autorii, data (în format `AN-LUNĂ-ZI`) și textul principal al articolului. Dă-mi răspunsul într-un format structurat (JSON)."
    4.  AI-ul îi returnează datele frumos aranjate.
    5.  **Filtru de calitate:** Scriptul verifică dacă articolul are o dată de publicare și dacă textul extras este suficient de lung. Articolele fără dată sau cu conținut nesemnificativ sunt ignorate.

### Cum se leagă totul? Logica de business și eficiența

Aici intervine partea cea mai deșteaptă. Scriptul nu procesează totul de la zero de fiecare dată.

1.  **Încarcă configurația:** Se conectează la o bază de date (Supabase) de unde ia lista cu site-urile pe care trebuie să le verifice.
2.  **Memorează ce a făcut:** Înainte de a începe, scriptul încarcă două fișiere locale:
    *   `scraped_articles_v2.json`: Conține toate articolele extrase în trecut. Orice link de aici va fi automat sărit pentru a evita duplicarea.
    *   `stare_scanare.json`: Un fel de "jurnal de bord". Aici notează pentru fiecare site care este data celui mai recent articol găsit la ultima rulare.
3.  **Scanează inteligent (pe bază de dată):** Pentru fiecare site, în loc să verifice toate articolele, face următorul lucru:
    *   Citește din `stare_scanare.json` care a fost ultima dată la care a găsit un articol (ex: `2024-08-15`).
    *   Începe să extragă articole noi și le compară data.
    *   **Se oprește devreme:** În momentul în care dă peste un articol cu data mai veche sau egală cu `2024-08-15`, consideră că a ajuns din urmă cu munca și se oprește, trecând la următorul site. Acest lucru economisește enorm timp și resurse.
    *   Dacă este prima scanare pentru un site, se uită în urmă doar un număr prestabilit de luni (ex: 12 luni).
4.  **Salvează rezultatele și actualizează starea:**
    *   Toate articolele noi, care au trecut de filtrele de calitate, sunt adăugate în `scraped_articles_v2.json`.
    *   La final, actualizează `stare_scanare.json` cu data celui mai nou articol găsit la rularea curentă pentru fiecare site.

Pe scurt, `simple_scraper.py` este un script modern și eficient care folosește inteligența artificială pentru a automatiza extragerea de articole, dar adaugă un strat de inteligență operațională prin managementul stării, asigurându-se că procesează doar conținutul nou și relevant.