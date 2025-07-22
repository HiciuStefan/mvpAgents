import os
import json
from datetime import datetime
from agents.website.scrape_index_links import extract_article_links
from agents.website.scraper import scrape_article
from agents._tools.llm_websiteAgent import analyze_article, load_user_profile
from agents.common.api_sender import ApiClient # MODIFICAT
from agents.common.context_api_fetcher import get_client_context
from agents.common.json_validator import validate_json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITES_FILE = os.path.join(SCRIPT_DIR, "..", "config", "website_config.json")
MAX_ARTICLES = 4
PROCESSED_FILE = "results/processed_articles.json"

# Inițializează clientul API o singură dată
website_api_client = ApiClient(
    api_endpoint_env="WEBSITE_AGENT_URL",
    api_key_env="WEBSITE_AGENT_API_KEY"
)

# Încarcă fișier JSON dacă există, altfel returnează listă goală
def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Salvează datele într-un fișier JSON
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Încarcă configurațiile din sites.json
def load_sites_config():
    if not os.path.exists(SITES_FILE):
        print(f"⚠️ Fișierul {SITES_FILE} nu există.")
        return {}
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Eroare la parsarea {SITES_FILE}.")
            return {}

# Verifică dacă articolul a mai fost procesat
def already_processed(processed, url):
    return any(article["url"] == url for article in processed)

# Procesează toate articolele pentru un client
def process_client(client_name, article_urls, selectors):
    print(f"Scraping site: {client_name}")

    processed_articles = load_json(PROCESSED_FILE)
    processed_urls = {a["url"] for a in processed_articles if a.get("client_name") == client_name}

    unique_urls = list(set(article_urls))[:MAX_ARTICLES]

    with open('agents/config/website_schema.json', 'r') as f:
        website_schema = json.load(f)

    for url in unique_urls:
        if url in processed_urls:
            print(f"⏭️ Deja procesat: {url}")
            continue

        print(f"Extragere articol: {url}")
        try:
            result = scrape_article(url, selectors)
            title = result.get("title", "Fără titlu")
            content = result.get("content", "")

            if not content or len(content) < 100:
                print("⚠️ Conținut insuficient. Trecem mai departe.")
                continue

            client_context = get_client_context(client_name)

            user_profile = load_user_profile()

            analysis_result = analyze_article(
                client_name=client_name,
                title=title,
                content=content,
                user_profile=user_profile
            )

            article_data = {
                "client_name": client_name,
                "url": url,
                "title": title,
                "content": content,
                "short_description": analysis_result["short_description"],
                "actionable": analysis_result["actionable"],
                "opportunity_type": analysis_result["opportunity_type"],
                "suggested_action": analysis_result["suggested_action"],
                "relevance": analysis_result["relevance"],
                "read": False,
                "scraped_at": datetime.now().isoformat()
            }

            is_valid, message = validate_json(article_data, website_schema)
            if is_valid:
                # Folosește clientul API centralizat
                if website_api_client.send_data(article_data):
                    print(f"✅ Articol trimis: {title}")
                    processed_articles.append(article_data)
                    save_json(PROCESSED_FILE, processed_articles) # Comentat pentru a nu salva local momentan
                else:
                    print(f"⚠️ Articolul nu a putut fi trimis sau există deja: {title}")
            else:
                print(f"JSON validation error: {message}")

        except Exception as e:
            print(f"Eroare la articolul {url}. Tip eroare: {type(e).__name__}")

# Funcția principală
def main():
    print("Pornim scraper-ul...")
    sites_config = load_sites_config()

    for site in sites_config:
        client_name = site["name"]
        selectors = site["selectors"]
        all_links = []

        for index_url in site["article_urls"]:
            links = extract_article_links(index_url)
            print(f"Gasite {len(links)} linkuri in {index_url}")
            all_links.extend(links)

        process_client(client_name, all_links, selectors)

    print("Gata! Toate articolele au fost procesate.")

if __name__ == "__main__":
    main()
