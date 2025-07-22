# Analiza Comparativă a Costurilor: Procesare Batch vs. Individuală

Acest document analizează diferențele de cost între cele două abordări de procesare a celor 11 iteme din scenarii, folosind modelul GPT-4o prin Azure OpenAI.

## 1. Modelul de Preț

Costurile pentru modelele lingvistice se bazează pe numărul de "tokeni" procesați. Un token este aproximativ echivalent cu 4 caractere de text în engleză. Prețul este diferit pentru tokenii trimiși către model (**input**) și cei primiți de la model (**output**).

Fiecare apel către LLM conține:
- **Prompt-ul de sistem:** Instrucțiunile fixe pe care le dăm AI-ului.
- **Contextul utilizatorului:** Fișierul `digital_excellence.json`.
- **Contextul RAG:** Informațiile extrase din baza de date vectorială.
- **Item-urile de procesat:** Conținutul efectiv (email, tweet, etc.).

## 2. Abordarea Batch (1 Apel API)

În această abordare, toate componentele sunt combinate într-un singur apel către LLM.

- **Avantaj:** Costul "fix" (prompt-ul de sistem și contextul utilizatorului, care sunt destul de mari) este plătit o singură dată. Este o metodă foarte eficientă din punct de vedere al costurilor.

## 3. Abordarea Individuală (11 Apeluri API)

Aici, procesul se repetă pentru fiecare item în parte.

- **Dezavantaj:** Costul fix (prompt-ul de sistem și contextul utilizatorului) este multiplicat cu numărul de iteme. Acest lucru duce la o creștere exponențială a costurilor.

---

## 4. Estimare de Cost Efectivă (USD)

Pentru a calcula costurile, vom estima numărul de tokeni pentru fiecare componentă. Folosim o rată de conversie de **1 token ≈ 4 caractere**.

### Estimare Tokeni (Componente de Bază)

- **Prompt Sistem (Batch):** ~3000 caractere ≈ **750 tokeni**
- **Prompt Sistem (Individual):** ~2500 caractere ≈ **625 tokeni**
- **Context Utilizator (`digital_excellence.json`):** ~1500 caractere ≈ **375 tokeni**
- **Total Scenarii (11 iteme):** ~4500 caractere ≈ **1125 tokeni**
- **Context RAG (estimare):** Să presupunem că RAG returnează un context de ~1000 caractere per căutare ≈ **250 tokeni**.
- **Output (estimare):** Să presupunem că LLM returnează în medie 200 de tokeni per item acționabil. Estimăm 8 iteme acționabile.

### Calcul Cost - Abordarea Batch

- **Input Tokens:** 750 + 375 + 250 + 1125 = **2500 tokeni**
- **Output Tokens:** 8 * 200 = **1600 tokeni**

### Calcul Cost - Abordarea Individuală

- **Input Tokens (per apel):** 625 + 375 + 250 + (1125 / 11) ≈ **1352 tokeni**
- **Total Input (11 apeluri):** 11 * 1352 = **14,872 tokeni**
- **Output Tokens (total):** 8 * 200 = **1600 tokeni**

### 5. Comparație de Prețuri între Modele

| Model                     | Preț Input ($/1M) | Preț Output ($/1M) | Cost Batch (Est.) | Cost Individual (Est.) |
| ------------------------- | ----------------- | ------------------ | ----------------- | ---------------------- |
| **OpenAI GPT-4o**         | **$5.00**         | **$15.00**         | **$0.0365**       | **$0.0984**            |
| **Anthropic Claude 3 Opus** | $15.00            | $75.00             | $0.1575           | $0.3431                |
| **Google Gemini 1.5 Pro** | $1.25             | $5.00              | $0.0111           | $0.0266                |
| **OpenAI GPT-4 Turbo**    | $10.00            | $30.00             | $0.0730           | $0.1967                |
| **OpenAI GPT-3.5 Turbo**  | $0.50             | $1.50              | $0.0037           | $0.0098                |

**Concluzie Finală:**

Abordarea **individuală** este de aproximativ **2.7 ori mai scumpă** decât cea **batch** pentru acest scenariu specific, folosind GPT-4o. Această diferență de cost se menține, și chiar se accentuează, la majoritatea modelelor de top.

**Google Gemini 1.5 Pro** se dovedește a fi cea mai economică opțiune dintre modelele de înaltă performanță, în timp ce **Anthropic Claude 3 Opus** este cea mai costisitoare pentru acest tip de sarcină.

Indiferent de modelul ales, **abordarea batch rămâne fundamental mai eficientă din punct de vedere economic**.