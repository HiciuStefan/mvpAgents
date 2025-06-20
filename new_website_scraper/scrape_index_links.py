from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_article_links(index_url):
    print(f"🔗 Accesez cu Playwright: {index_url}")

    # 🔹 Listă flexibilă de cuvinte care apar frecvent în linkurile articolelor
    link_filters = ["/solutions/", "/blog/", "/news/", "/article", "/post", "/insights", "/update"]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(index_url, timeout=60000)

            # Așteptăm pentru încărcare completă
            page.wait_for_timeout(7000)
            page.screenshot(path="debug.png")  # opțional pentru verificare

            html = page.content()
            browser.close()

    except Exception as e:
        print(f"⚠️ Eroare Playwright: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = []

    parsed_base = urlparse(index_url)
    base_domain = parsed_base.netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(index_url, href)
        parsed = urlparse(full_url)

        # 🔸 Reguli de filtrare inteligente:
        if (
            parsed.netloc == base_domain and
            any(f in parsed.path for f in link_filters) and
            not href.startswith("#") and
            not parsed.path.endswith("/") and
            len(parsed.path.strip("/").split("/")) >= 2  # minim 2 niveluri în path
        ):
            links.append(full_url)

    unique_links = list(set(links))
    print(f"✅ Găsite {len(unique_links)} linkuri care trec filtrul flexibil.")
    return unique_links
