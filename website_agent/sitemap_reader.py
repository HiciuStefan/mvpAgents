import requests
import xml.etree.ElementTree as ET
import json
import os

SITE_CONFIG_PATH = "site_config.json"

def is_article_url(url):
    keywords = ["/news/", "/blog/", "/article", "/press", "/stories", "/post", "/content", "/insights", "/updates", "/latest"]
    return any(keyword in url.lower() for keyword in keywords)

def fetch_sitemap_urls(base_url):
    try:
        # Sitemap index presupus implicit
        index_url = base_url.rstrip("/") + "/sitemap.xml"
        response = requests.get(index_url, timeout=10)

        if response.status_code != 200:
            return {
                "sitemap_found": False,
                "sitemap_url": index_url,
                "article_urls": [],
                "fallback_used": False
            }

        root = ET.fromstring(response.content)
        first_sitemap = root.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if first_sitemap is not None:
            sitemap_url = first_sitemap.text
            sitemap_response = requests.get(sitemap_url, timeout=10)
            sitemap_root = ET.fromstring(sitemap_response.content)
        else:
            sitemap_url = index_url
            sitemap_root = root  # Folosește direct sitemap-ul inițial

        urls = [
            loc.text for loc in sitemap_root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if is_article_url(loc.text)
        ]

        return {
            "sitemap_found": True,
            "sitemap_url": sitemap_url,
            "article_urls": urls,
            "fallback_used": False
        }

    except Exception as e:
        print(f"❌ Eroare la citirea sitemap pentru {base_url}: {e}")
        return {
            "sitemap_found": False,
            "sitemap_url": "",
            "article_urls": [],
            "fallback_used": False
        }

def update_site_config():
    if not os.path.exists(SITE_CONFIG_PATH):
        print("❌ Fișierul site_config.json nu există.")
        return

    with open(SITE_CONFIG_PATH, "r", encoding="utf-8") as f:
        sites = json.load(f)

    for site in sites:
        print(f"🔍 Analizăm: {site['base_url']} ...")
        result = fetch_sitemap_urls(site["base_url"])

        site["sitemap_url"] = result["sitemap_url"]
        site["sitemap_found"] = result["sitemap_found"]
        site["fallback_used"] = result["fallback_used"]
        site["article_urls"] = result["article_urls"]
        site["articles_found"] = len(result["article_urls"])

        print(f"✅ Găsite {site['articles_found']} articole relevante.")

    with open(SITE_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    update_site_config()
