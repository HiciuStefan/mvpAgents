from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # timp pentru JS să încarce
        html = page.content()
        browser.close()
    return html

def extract_with_selectors(soup, selectors):
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            texts = []
            for el in elements:
                text = el.get_text(strip=True)
                if len(text) > 5:
                    texts.append(text)
            if texts:
                return "\n\n".join(texts)
    return None

def extract_title_fallback(soup):
    # Încearcă taguri utile
    for tag in ["h1", "div[class*='title']", "header h1", "div[class*='headline']"]:
        found = soup.select_one(tag)
        if found:
            return found.get_text(strip=True)

    # Fallback absolut: <title> din <head>
    if soup.title:
        raw_title = soup.title.get_text(strip=True)

        # 🔻 Curățare: oprește la primul "|"
        clean_title = raw_title.split("|")[0].strip()

        return clean_title

    return "Fără titlu"


def scrape_article(url, selectors):
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    # 🔻 Elimină zgomotul: cookies, consent etc.
    for bad in soup.select('[id*="cookie"], [class*="cookie"], [id*="consent"], [class*="consent"]'):
        bad.decompose()

    # 🔻 Titlu: încearcă întâi selectorii, apoi fallback
    title = extract_with_selectors(soup, selectors.get("title", [])) or extract_title_fallback(soup)

    # 🔻 Conținut: încearcă selectorii specifici
    content = extract_with_selectors(soup, selectors.get("content", []))

    # 🔻 Fallback: extrage tot textul, filtrat
    if not content:
        print("⚠️ Fallback: extragere text brut filtrat")
        raw_texts = soup.stripped_strings
        unwanted_keywords = ["cookie", "consent", "privacy", "targeting", "functional", "performance"]
        filtered = [
            t for t in raw_texts
            if len(t) > 40 and not any(word in t.lower() for word in unwanted_keywords)
        ]
        content = "\n\n".join(filtered)

    return {
        "url": url,
        "title": title,
        "content": content[:5000]  # limită pentru AI / API / UI
    }
