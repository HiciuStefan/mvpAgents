import json
import os
from datetime import datetime
from scraper import scrape_article
from scrape_index_links import extract_article_links
from semantic_analyzer import analyze_article
from api_client import send_article_to_api


CONFIG_FILE = "config/sites.json"
PROCESSED_FILE = "results/processed_articles.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def already_processed(processed, url):
    return any(article["url"] == url for article in processed)

def main():
    print("🚀 Pornim scraper-ul...")

    sites = load_json(CONFIG_FILE)
    processed_articles = load_json(PROCESSED_FILE)

    for site in sites:
        print(f"\n🔎 Scraping site: {site['name']}")

        article_urls = []
        for index_url in site["article_urls"]:
            links = extract_article_links(index_url)
            print(f"🔗 Găsite {len(links)} linkuri în {index_url}")
            article_urls.extend(links)

        # 🔹 Limitează la maximumum 10 linkuri (configurabil dacă vrei)
        article_urls = list(set(article_urls))[:10]

        for article_url in article_urls:
            if already_processed(processed_articles, article_url):
                print(f"⏭️ Deja procesat: {article_url}")
                continue

            try:
                print(f"\n📄 Extragere articol: {article_url}")
                result = scrape_article(article_url, site["selectors"])
                short_description, actionable, opportunity_type, suggested_action, relevance = analyze_article(
    result["title"], result["content"]
)


                article_data = {
                    "client_name": site["name"],
                    "url": result["url"],
                    "title": result["title"],
                    "content": result["content"],
                    "short_description": short_description,
                    "actionable": actionable,
                    "opportunity_type": opportunity_type,
                    "suggested_action": suggested_action,
                    "relevance": relevance,
                    "read": False,
                    "scraped_at": datetime.now().isoformat()
                }


                processed_articles.append(article_data)
                send_article_to_api(article_data)
                print(f"✅ Articol salvat și trimis: {result['title']}")

            except Exception as e:
                print(f"⚠️ Eroare la articol: {e}")

    save_json(PROCESSED_FILE, processed_articles)
    print("\n🎉 Gata! Toate articolele au fost procesate.")


if __name__ == "__main__":
    main()
