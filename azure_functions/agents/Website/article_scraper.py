import os
import sys
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from bs4.element import Tag

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from llm_client import llm
from blog_index_processor import BlogIndexProcessor

SCRAPING_STATE_FILENAME = "/tmp/scraping_state.json"
OUTPUT_FILENAME = "/tmp/scraped_articles.json"

EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.mp4', '.avi', '.mov')
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

def get_client_key(client_name: str, base_url: str) -> str:
    return f"{client_name}|{base_url}" if client_name else base_url

class ArticleData(BaseModel):
    title: str = Field(description="The main title of the article.")
    authors: Optional[List[str]] = Field(description="List of authors of the article.")
    text: str = Field(description="The full, cleaned text content of the article.")
    publish_date: Optional[str] = Field(description="The publication date of the article in YYYY-MM-DD format. If no date is found, this should be null.")

class DateSelector(BaseModel):
    selector: Optional[str] = Field(description="A specific CSS selector to find the publication date element. Should be null if no reliable selector can be found.")

class ArticleScraperV3:
    def __init__(self, output_filename=OUTPUT_FILENAME):
        self.output_path = os.path.join(os.path.dirname(__file__), output_filename)
        self.state_path = os.path.join(os.path.dirname(__file__), SCRAPING_STATE_FILENAME)
        self.processed_urls = self._load_processed_urls()
        self.scraping_state = self._load_scraping_state()
        self.blog_index_processor = BlogIndexProcessor()

    def _is_http_url(self, href: str) -> bool:
        href_lower = href.lower()
        if href_lower.startswith("mailto:") or href_lower.startswith("tel:") or href_lower.startswith("javascript:"):
            return False
        return True

    def _normalize_netloc(self, netloc: str) -> str:
        return netloc[4:] if netloc.startswith("www.") else netloc

    def _is_internal(self, base_url: str, candidate_url: str) -> bool:
        base_netloc = self._normalize_netloc(urlparse(base_url).netloc)
        cand_netloc = self._normalize_netloc(urlparse(candidate_url).netloc)
        return cand_netloc == base_netloc or cand_netloc.endswith("." + base_netloc)

    def _load_processed_urls(self) -> set:
        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
            return {a.get("url") for a in articles if "url" in a}
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def _load_scraping_state(self) -> dict:
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_scraping_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.scraping_state, f, indent=2, ensure_ascii=False)

    def _save_articles(self, articles: List[dict]):
        try:
            existing = []
            if os.path.exists(self.output_path):
                with open(self.output_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(existing + articles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save articles: {e}")

    def _get_html(self, url: str) -> Optional[str]:
        import requests
        try:
            resp = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

    def find_individual_article_links(self, blog_index_url: str, excluded_index_urls: Optional[set] = None) -> List[str]:
        from collections import deque
        excluded_index_urls = excluded_index_urls or set()
        visited = set()
        index_parsed = urlparse(blog_index_url)
        base_root = f"{index_parsed.scheme}://{index_parsed.netloc}"
        index_path = index_parsed.path.rstrip('/')
        index_segments = [seg for seg in index_path.split('/') if seg]
        queue = deque([(blog_index_url, 0)])
        article_candidates = set()
        while queue:
            current_url, depth = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)
            html_content = self._get_html(current_url)
            if not html_content:
                continue
            soup = BeautifulSoup(html_content, "html.parser")
            for a in soup.find_all("a", href=True):
                if not isinstance(a, Tag):
                    continue
                href_attr = a.attrs.get("href", "")
                href = href_attr.strip() if isinstance(href_attr, str) else str(href_attr)
                if not self._is_http_url(href):
                    continue
                abs_url = urljoin(current_url, href)
                if abs_url in excluded_index_urls:
                    continue
                if not self._is_internal(blog_index_url, abs_url):
                    continue
                p = urlparse(abs_url)
                segs = [s for s in p.path.split('/') if s]
                if segs and len(segs[0]) == 2 and segs[0].isalpha() and segs[0].lower() not in {'en','ro'}:
                    continue
                if abs_url.lower().endswith(EXTENSIONS):
                    continue
                parsed = urlparse(abs_url)
                if not parsed.path.startswith(index_path):
                    continue
                path = parsed.path.rstrip('/')
                segments = [seg for seg in path.split('/') if seg]
                is_index_like = (
                    ('page' in segments[-1].lower() if segments else False) or
                    (len(segments) >= 2 and 'page' in segments[-2].lower()) or
                    path.endswith('/category') or '/category/' in path or '/tag/' in path or
                    (len(segments) >= 3 and segments[0] == 'c' and 'page' in segments[-1].lower())
                )
                looks_like_article = len(segments) >= len(index_segments) + 1 and not is_index_like
                if looks_like_article:
                    article_candidates.add(abs_url)
                if is_index_like or (len(segments) <= len(index_segments) + 2 and depth < 2):
                    if abs_url not in visited:
                        queue.append((abs_url, depth + 1))
        return list(article_candidates)

    def _find_date_selector_with_llm(self, article_url: str) -> Optional[str]:
        html_content = self._get_html(article_url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, "html.parser")
        # Clean the HTML for better LLM processing
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        body_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
        
        try:
            parser = JsonOutputParser(pydantic_object=DateSelector)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert in web scraping. Your task is to find the most reliable CSS selector for the publication date of an article given its HTML content. The selector should be specific enough to avoid other dates. Prioritize selectors with attributes like `[itemprop='datePublished']`, `[property='article:published_time']`, or classes/IDs related to 'date', 'published', 'meta'. If no reliable selector can be found, return null."),
                ("human", "Article URL: {url}\nHTML Body (cleaned):\n{snippet}\n\nReturn JSON with the CSS selector: {format}")
            ])
            chain = prompt | llm | parser
            
            # Provide a significant snippet of the body
            snippet = body_text[:8000]
            
            result = chain.invoke({
                "url": article_url,
                "snippet": snippet,
                "format": parser.get_format_instructions()
            })
            
            selector = result.get("selector") if isinstance(result, dict) else None
            if selector and isinstance(selector, str):
                print(f"[INFO] LLM identified date selector: '{selector}'")
                return selector
            return None
        except Exception as e:
            print(f"[ERROR] LLM failed to find date selector for {article_url}: {e}")
            return None

    def extract_article_data(self, url: str, date_selector: Optional[str]) -> Optional[dict]:
        html_content = self._get_html(url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        if not title:
            h1 = soup.find('h1')
            title = h1.get_text(strip=True) if h1 else ""
        
        text = soup.get_text(separator="\n", strip=True)
        publish_date: Optional[str] = None

        # 1. Use the provided CSS selector first
        if date_selector:
            date_element = soup.select_one(date_selector)
            if date_element:
                date_text = date_element.get('datetime') or date_element.get_text(strip=True)
                if date_text:
                    m = re.search(r"\d{4}-\d{2}-\d{2}", str(date_text))
                    if m:
                        publish_date = m.group(0)
        
        # 2. Fallback to existing methods if selector fails or is not present
        if not publish_date:
            meta_selectors = [
                ("meta", {"property": "article:published_time"}),
                ("meta", {"name": "publish_date"}),
                ("time", {"datetime": True}),
            ]
            for tag, attrs in meta_selectors:
                el = soup.find(tag, attrs)
                if el and isinstance(el, Tag):
                    val = el.attrs.get("content") or el.attrs.get("datetime")
                    if isinstance(val, str):
                        m = re.search(r"\d{4}-\d{2}-\d{2}", val)
                        if m:
                            publish_date = m.group(0)
                            break
        
        if not publish_date:
            # Fallback to regex on the whole HTML
            date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", html_content)
            publish_date = date_match.group(0) if date_match else None

        return {
            "url": url,
            "title": title,
            "authors": [],
            "text": text,
            "publish_date": publish_date
        }

    def run(self, base_url: str, client_name: str):
        client_key = get_client_key(client_name, base_url)
        if client_key not in self.scraping_state:
            print(f"[INFO] {client_key} not found in scraping_state. Running BlogIndexProcessor...")
            self.blog_index_processor.process_website(base_url, client_name, self.scraping_state)
            self._save_scraping_state()

        client_state = self.scraping_state.get(client_key, {})
        blog_index_urls = client_state.get("blog_index_urls", [])
        rejected_index_urls = set(client_state.get("rejected_index_urls", []))
        
        if not blog_index_urls:
            print(f"[WARN] No blog index URLs found for {base_url}.")
            return

        # Determine or find the date selector for this client
        date_selector = client_state.get("date_selector")
        if not date_selector:
            print(f"[INFO] No date selector found for {client_key}. Attempting to find one with LLM.")
            # Find a selector using the first article of the first index page
            if blog_index_urls:
                first_index_links = self.find_individual_article_links(blog_index_urls[0], rejected_index_urls)
                if first_index_links:
                    date_selector = self._find_date_selector_with_llm(first_index_links[0])
                    if date_selector:
                        self.scraping_state.setdefault(client_key, {})["date_selector"] = date_selector
                        self._save_scraping_state()
                else:
                    print(f"[WARN] Could not find any article links on {blog_index_urls[0]} to determine a date selector.")

        latest_state_date_str = client_state.get("latest_article_date")
        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=183)
        if latest_state_date_str:
            try:
                cutoff_dt = datetime.strptime(latest_state_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"[WARN] Invalid date format in state. Using 6-month lookback.")
        
        print(f"[INFO] Using cutoff date: {cutoff_dt.date()}")

        new_articles = []
        newest_dt_found: Optional[datetime] = None
        for blog_index_url in blog_index_urls:
            article_links = self.find_individual_article_links(blog_index_url, excluded_index_urls=rejected_index_urls)
            print(f"[INFO] Found {len(article_links)} potential articles in {blog_index_url}.")
            
            for article_url in article_links:
                if article_url in self.processed_urls:
                    continue
                
                article_data = self.extract_article_data(article_url, date_selector)
                if not (article_data and article_data.get("publish_date")):
                    continue

                try:
                    art_dt = datetime.strptime(article_data["publish_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

                if art_dt >= cutoff_dt:
                    new_articles.append(article_data)
                    self.processed_urls.add(article_url)
                    if newest_dt_found is None or art_dt > newest_dt_found:
                        newest_dt_found = art_dt
        
        if new_articles:
            self._save_articles(new_articles)
            print(f"[INFO] Saved {len(new_articles)} new articles.")
            if newest_dt_found:
                newest_str = newest_dt_found.strftime("%Y-%m-%d")
                # Update state only if the newest found date is later than the one in the state
                if not latest_state_date_str or newest_dt_found > datetime.strptime(latest_state_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc):
                    self.scraping_state.setdefault(client_key, {})["latest_article_date"] = newest_str
                    self._save_scraping_state()
                    print(f"[INFO] Updated latest_article_date to {newest_str}")
        else:
            print("[INFO] No new articles found meeting the criteria.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python article_scraping.py [base_url] [client_name]")
        sys.exit(1)
    target_base_url = sys.argv[1]
    client_name = sys.argv[2]
    scraper = ArticleScraperV3()
    scraper.run(target_base_url, client_name)
