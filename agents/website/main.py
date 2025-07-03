import os
import json
from datetime import datetime
from .scrape_index_links import extract_article_links
from .scraper import scrape_article
from agents._tools.llm_websiteAgent import analyze_article, load_user_profile
from .api_client import send_article_to_api
from .context_api_fetcher import get_client_context

SITES_FILE = "config/sites.json"
MAX_ARTICLES = 4
PROCESSED_FILE = "results/processed_articles.json"

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
    print(f"\n🔎 Scraping site: {client_name}")

    processed_articles = load_json(PROCESSED_FILE)
    processed_urls = {a["url"] for a in processed_articles if a.get("client_name") == client_name}

    unique_urls = list(set(article_urls))[:MAX_ARTICLES]

    for url in unique_urls:
        if url in processed_urls:
            print(f"⏭️ Deja procesat: {url}")
            continue

        print(f"\n📄 Extragere articol: {url}")
        try:
            result = scrape_article(url, selectors)
            title = result.get("title", "Fără titlu")
            content = result.get("content", "")

            if not content or len(content) < 100:
                print("⚠️ Conținut insuficient. Trecem mai departe.\n")
                continue

            client_context = get_client_context(client_name)

            user_profile = load_user_profile("digital_excellence")

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

            send_article_to_api(article_data)
            processed_articles.append(article_data)
            # save_json(PROCESSED_FILE, processed_articles)
            print(f"✅ Articol salvat și trimis: {title}")

            # was_sent = send_article_to_api(article_data)

            # if was_sent:
            #     print(f"✅ Articol salvat și trimis: {title}")
            # else:
            #     print(f"⚠️ Articol NEtrimis: {title}")


        except Exception as e:
            print(f"⚠️ Eroare la articol: {e}")

# Funcția principală
def main():
    print("🚀 Pornim scraper-ul...")
    sites_config = load_sites_config()
    processed_articles = load_json(PROCESSED_FILE)

    for site in sites_config:
        client_name = site["name"]
        selectors = site["selectors"]
        all_links = []

        for index_url in site["article_urls"]:
            links = extract_article_links(index_url)
            print(f"🔗 Găsite {len(links)} linkuri în {index_url}")
            all_links.extend(links)

        process_client(client_name, all_links, selectors)

    print("\n🎉 Gata! Toate articolele au fost procesate.")

if __name__ == "__main__":
    main()
