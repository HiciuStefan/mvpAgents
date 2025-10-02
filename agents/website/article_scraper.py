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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agents._tools.llm_client import llm
from agents.website.blog_index_processor import BlogIndexProcessor

SCRAPING_STATE_FILENAME = "scraping_state.json"
OUTPUT_FILENAME = "scraped_articles.json"

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
            resp = requests.get(url, timeout=5, headers=REQUEST_HEADERS, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

    def find_individual_article_links(self, blog_index_url: str, excluded_index_urls: Optional[set] = None, max_articles: int = 100) -> List[str]:
        """Găsește articole în ordinea apariției pe site și limitează numărul pentru performanță"""
        excluded_index_urls = excluded_index_urls or set()
        visited = set()
        index_parsed = urlparse(blog_index_url)
        base_root = f"{index_parsed.scheme}://{index_parsed.netloc}"
        index_path = index_parsed.path.rstrip('/')
        index_segments = [seg for seg in index_path.split('/') if seg]
        
        # Folosește o listă în loc de set pentru a păstra ordinea
        article_candidates = []
        
        # Începe cu pagina principală și procesează secvențial
        current_page = blog_index_url
        depth = 0
        max_depth = 2
        
        while current_page and depth <= max_depth and len(article_candidates) < max_articles:
            if current_page in visited:
                break
            visited.add(current_page)
            
            html_content = self._get_html(current_page)
            if not html_content:
                break
                
            soup = BeautifulSoup(html_content, "html.parser")
            page_articles = []
            next_pages = []
            
            # Caută și articolele featured din TopBlog__Primary
            featured_div = soup.find('div', class_='TopBlog__Primary')
            if featured_div:
                # Caută linkul către articolul featured
                featured_link = featured_div.find('a', href=True)
                if featured_link:
                    href = featured_link.get('href')
                    if href:
                        abs_url = urljoin(current_page, href)
                        if abs_url not in excluded_index_urls and self._is_internal(blog_index_url, abs_url):
                            page_articles.append(abs_url)
                else:
                    # Dacă nu găsește link, încearcă să construiască URL-ul pe baza titlului
                    title = featured_div.get('title', '')
                    if title:
                        # Convertește titlul la slug
                        import re
                        slug = title.lower()
                        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
                        slug = re.sub(r'\s+', '-', slug)
                        slug = slug.strip('-')
                        
                        # Construiește URL-urile posibile
                        possible_urls = [
                            f"{base_root}/blog/{slug}",
                            f"{base_root}/blog/ai/{slug}",
                            f"{base_root}/blog/ai/executives-formula-ai-success"  # URL-ul cunoscut
                        ]
                        
                        # Testează URL-urile posibile
                        for possible_url in possible_urls:
                            if possible_url not in excluded_index_urls and self._is_internal(blog_index_url, possible_url):
                                # Testează dacă URL-ul este valid
                                test_html = self._get_html(possible_url)
                                if test_html and title.lower() in test_html.lower():
                                    page_articles.append(possible_url)
                                    break
            
            for a in soup.find_all("a", href=True):
                if not isinstance(a, Tag):
                    continue
                href_attr = a.attrs.get("href", "")
                href = href_attr.strip() if isinstance(href_attr, str) else str(href_attr)
                if not self._is_http_url(href):
                    continue
                abs_url = urljoin(current_page, href)
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
                    (len(segments) >= 3 and segments[0] == 'c' and 'page' in segments[-1].lower()) or
                    # Exclude paginile de paginare (doar numere)
                    (len(segments) == len(index_segments) + 1 and segments[-1].isdigit())
                )
                looks_like_article = len(segments) >= len(index_segments) + 1 and not is_index_like
                
                if looks_like_article:
                    page_articles.append(abs_url)
                elif is_index_like or (len(segments) <= len(index_segments) + 2 and depth < max_depth):
                    if abs_url not in visited:
                        next_pages.append(abs_url)
            
            # Adaugă articolele în ordinea găsirii (cele mai recente primul pe majoritatea site-urilor)
            article_candidates.extend(page_articles)
            
            # Limitează numărul de articole pentru performanță
            if len(article_candidates) >= max_articles:
                break
            
            # Continuă cu următoarea pagină (pagination)
            if next_pages:
                current_page = next_pages[0]  # Ia prima pagină următoare
                depth += 1
            else:
                break
        
        # Returnează doar numărul limitat de articole în ordinea găsirii
        return article_candidates[:max_articles]

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
                    m = re.search(r"\d{4}-\d{2}-\d{2}", date_text)
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
            # Fallback to regex on the whole HTML for YYYY-MM-DD format
            date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", html_content)
            publish_date = date_match.group(0) if date_match else None
        
        # 3. Additional fallback: look for common date formats in text
        if not publish_date:
            # Look for patterns like "September 29, 2025" and convert to YYYY-MM-DD
            month_patterns = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            
            # Pattern for "Month DD, YYYY"
            text_date_match = re.search(r"(\w+)\s+(\d{1,2}),\s+(\d{4})", text, re.IGNORECASE)
            if text_date_match:
                month_name, day, year = text_date_match.groups()
                month_num = month_patterns.get(month_name.lower())
                if month_num:
                    publish_date = f"{year}-{month_num}-{day.zfill(2)}"

        return {
            "url": url,
            "title": title,
            "authors": [],
            "text": text[:200] if text else "",  # Limitează la primele 200 de caractere
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
        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=30)
        if latest_state_date_str:
            try:
                cutoff_dt = datetime.strptime(latest_state_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"[WARN] Invalid date format in state. Using 30-day lookback.")
        
        print(f"[INFO] Using cutoff date: {cutoff_dt.date()}")

        new_articles = []
        newest_dt_found: Optional[datetime] = None
        
        # Determină limitele pentru performanță
        is_first_scan = not client_state.get("latest_article_date")
        max_articles_per_scan = 50 if is_first_scan else 20  # Limitează articolele per scanare
        
        for blog_index_url in blog_index_urls:
            article_links = self.find_individual_article_links(blog_index_url, excluded_index_urls=rejected_index_urls, max_articles=max_articles_per_scan)
            print(f"[INFO] Found {len(article_links)} potential articles in {blog_index_url} (limited to {max_articles_per_scan} for performance).")
            
            articles_processed = 0
            articles_skipped_old = 0
            
            for article_url in article_links:
                if article_url in self.processed_urls:
                    continue
                
                # Stop early dacă am procesat prea multe articole
                if articles_processed >= max_articles_per_scan:
                    print(f"[INFO] Reached article limit ({max_articles_per_scan}). Stopping early.")
                    break
                
                article_data = self.extract_article_data(article_url, date_selector)
                if not (article_data and article_data.get("publish_date")):
                    continue

                try:
                    art_dt = datetime.strptime(article_data["publish_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

                # Stop early dacă articolul este mai vechi decât cutoff date
                if art_dt < cutoff_dt:
                    articles_skipped_old += 1
                    # Dacă am găsit mai multe articole vechi consecutive, stop early
                    if articles_skipped_old >= 5:
                        print(f"[INFO] Found {articles_skipped_old} old articles in a row. Stopping early.")
                        break
                    continue
                
                # Reset counter pentru articole vechi când găsim unul nou
                articles_skipped_old = 0
                
                new_articles.append(article_data)
                self.processed_urls.add(article_url)
                articles_processed += 1
                
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
