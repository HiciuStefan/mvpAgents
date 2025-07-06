import os
import json
from datetime import datetime
from agents.website.scrape_index_links import extract_article_links
from agents.website.scraper import scrape_article
from agents._tools.llm_websiteAgent import analyze_article, load_user_profile
from agents.common.api_sender import ApiClient # MODIFICAT
from agents.common.context_api_fetcher import get_client_context

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITES_FILE = os.path.join(SCRIPT_DIR, "..", "config", "website_config.json")
MAX_ARTICLES = 4

# Inițializează clientul API o singură dată
website_api_client = ApiClient(
    api_endpoint_env="WEBSITE_AGENT_URL",
    api_key_env="WEBSITE_AGENT_API_KEY"
)

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

# Helper pentru a printa în siguranță pe Windows
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', 'replace').decode('utf-8'))

# Procesează toate articolele pentru un client
def process_client(client_name, article_urls, selectors):
    safe_print(f"\nScraping site: {client_name}")

    unique_urls = list(set(article_urls))[:MAX_ARTICLES]

    for url in unique_urls:
        safe_print(f"\nExtragere articol: {url}")
        try:
            result = scrape_article(url, selectors)
            title = result.get("title", "Fără titlu")
            content = result.get("content", "")

            if not content or len(content) < 100:
                print("⚠️ Conținut insuficient. Trecem mai departe.\n")
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

            # Folosește clientul API centralizat
            if website_api_client.send_data(article_data):
                safe_print(f"✅ Articol trimis: {title}")
            else:
                safe_print(f"Warning: Articolul nu a putut fi trimis sau există deja: {title}")

        except Exception as e:
            safe_print(f"Eroare la articol: {e}")

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

    print("\nGata! Toate articolele au fost procesate.")

if __name__ == "__main__":
    main()
