from playwright.sync_api import sync_playwright
import time

def extract_article_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        time.sleep(5)

        try:
            # Încercare 1: pentru TechCrunch
            paragraphs = page.locator("div.article-content p")
            count = paragraphs.count()
            content = []

            for i in range(count):
                text = paragraphs.nth(i).inner_text()
                content.append(text.strip())

            full_text = "\n\n".join(content)

            # Fallback dacă nu s-a găsit nimic
            if not full_text.strip():
                paragraphs = page.locator("p")
                count = paragraphs.count()
                content = []
                for i in range(count):
                    text = paragraphs.nth(i).inner_text()
                    content.append(text.strip())
                full_text = "\n\n".join(content)

        except Exception as e:
            full_text = f"❌ Nu s-a putut extrage conținutul: {e}"

        browser.close()
        return full_text
