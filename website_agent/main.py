import json
import os
from datetime import datetime
from sitemap_reader import update_site_config
from scraping.scrape_full_article import extract_article_content
from analysis.semantic_analyzer import analyze_article


PROCESSED_FILE = "processed_articles.json"
SITE_CONFIG_FILE = "site_config.json"

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_processed(processed):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

def already_processed(processed, url):
    return any(article["url"] == url for article in processed)

def extract_title_from_url(url):
    slug = url.rstrip("/").split("/")[-1].replace("-", " ")
    return slug.capitalize()

def save_article_to_processed(processed, url, content, title="", client_name="Unknown", date=None):
    if not title:
        title = extract_title_from_url(url)

    # Analizăm articolul pentru a obține sumarul, labelul și sugestia
    summary, label, opportunity_type, suggested_action = analyze_article(title, content)

    processed.append({
        "client_name": client_name,
        "url": url,
        "title": title,
        "content": content,
        "summary": summary,
        "label": label,
        "opportunity_type": opportunity_type,
        "suggested_action": suggested_action,
        "read": False,
        "scraped_at": date or datetime.now().isoformat()
    })

def main():
    print("🔍 Pornim Website Scraper Agent...")

    update_site_config()

    processed_articles = load_processed()

    with open(SITE_CONFIG_FILE, "r", encoding="utf-8") as f:
        sites = json.load(f)

    for site in sites:
        print(f"\n🌐 {site['name']} ({site['base_url']})")
        for i, url in enumerate(site.get("article_urls", []), 1):
            if already_processed(processed_articles, url):
                continue

            print(f"\n🔍 Articol {i}")
            print(f"🔗 {url}")

            try:
                content = extract_article_content(url)
                print(f"📃 Conținut extras:\n{content[:500]}...\n")
                if content:
                    client_name = site.get("name", "Unknown")  # 🔹 AICI
                    save_article_to_processed(processed_articles, url, content, client_name=client_name)

            except Exception as e:
                print(f"⚠️ Eroare la procesarea articolului: {e}")

    save_processed(processed_articles)
    print("\n✅ Procesare completă.")

if __name__ == "__main__":
    main()
