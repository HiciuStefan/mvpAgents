import os
import json
import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta, date
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from typing import List, Optional

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from supabase_retriever import load_json_from_supabase
from agents._tools.llm_client import llm

# --- Constants ---
STATE_FILENAME = "stare_scanare.json"
LOOKBACK_MONTHS = 12

# --- Pydantic Models for Structured Output ---

class ArticleData(BaseModel):
    """Pydantic model for structuring scraped article data."""
    title: str = Field(description="The main title of the article.")
    authors: Optional[List[str]] = Field(description="List of authors of the article.")
    publish_date: Optional[str] = Field(description="The publication date in YYYY-MM-DD format.")
    text: str = Field(description="The full, cleaned text content of the article.")

class ArticleLinks(BaseModel):
    """Pydantic model for a list of article URLs."""
    urls: List[str] = Field(description="A list of direct URLs to news or blog articles.")


# --- Core Scraper Class ---

class SimpleWebsiteScraper:
    def __init__(self, output_filename="scraped_articles_v2.json"):
        self.output_path = os.path.join(os.path.dirname(__file__), output_filename)
        self.state_path = os.path.join(os.path.dirname(__file__), STATE_FILENAME)
        self.processed_urls = self._load_processed_urls()
        self.scraping_state = self._load_scraping_state()

    def _load_processed_urls(self):
        """Loads URLs from the existing output file to avoid re-scraping."""
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                return {article['url'] for article in articles}
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def _load_scraping_state(self):
        """Loads the scraping state, like the last scraped date for each site."""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[INFO] State file '{STATE_FILENAME}' not found. A new one will be created.")
            return {}

    def _save_scraping_state(self):
        """Saves the updated scraping state to the file."""
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.scraping_state, f, indent=2)
        print(f"[INFO] Scraping state saved to {self.state_path}")

    def _get_html(self, url: str) -> Optional[str]:
        """Fetches the HTML content of a URL."""
        try:
            if url.startswith("hhttps"):
                url = url.replace("hhttps", "https")
            response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
            return None

    def find_blog_index_url(self, base_url: str) -> Optional[str]:
        """Uses an LLM to find the main blog/news index URL from a base URL."""
        print(f"[INFO] Finding blog index on {base_url}...")
        html_content = self._get_html(base_url)
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
        domain = urlparse(base_url).netloc
        internal_links = {link for link in all_links if urlparse(link).netloc == domain}

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert web navigator. From the list of links provided, identify the single URL that is most likely the main index page for a blog, news, or articles section. Return only the URL and nothing else."),
            ("human", "Base URL: {base_url}\n\nLinks:\n{links}")
        ])
        
        chain = prompt | llm
        try:
            response = chain.invoke({
                "base_url": base_url,
                "links": "\n".join(sorted(list(internal_links))[:150])
            })
            blog_index_url = response.content.strip()
            print(f"[INFO] LLM identified blog index: {blog_index_url}")
            return blog_index_url
        except Exception as e:
            print(f"[ERROR] LLM failed to find blog index: {e}")
            return None

    def find_individual_article_links(self, blog_index_url: str) -> List[str]:
        """Uses an LLM to find and list all direct article links from a news/blog index page."""
        print(f"[INFO] Finding individual article links on {blog_index_url}...")
        html_content = self._get_html(blog_index_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = [urljoin(blog_index_url, a['href']) for a in soup.find_all('a', href=True)]
        domain = urlparse(blog_index_url).netloc
        internal_links = {link for link in all_links if urlparse(link).netloc == domain}

        parser = JsonOutputParser(pydantic_object=ArticleLinks)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert web scraper. From the list of links, identify all direct links to individual blog posts or news articles. Exclude links to categories, author pages, or other index pages. Return a JSON object with the URLs."),
            ("human", "Blog Index URL: {blog_index_url}\n\nLinks:\n{links}\n\n{format_instructions}")
        ])

        chain = prompt | llm | parser
        try:
            response = chain.invoke({
                "blog_index_url": blog_index_url,
                "links": "\n".join(sorted(list(internal_links))[:150]),
                "format_instructions": parser.get_format_instructions()
            })
            print(f"[INFO] Found {len(response['urls'])} potential article links.")
            return response['urls']
        except Exception as e:
            print(f"[ERROR] LLM failed to extract individual article links: {e}")
            return []

    def extract_article_data(self, url: str) -> Optional[dict]:
        """
        Uses an LLM to extract structured data (title, author, date, text) from an article's HTML.
        """
        print(f"[INFO] Scraping article: {url}")
        html_content = self._get_html(url)
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        cleaned_html = str(soup)
        body_text = soup.get_text(separator='\n', strip=True)

        parser = JsonOutputParser(pydantic_object=ArticleData)
        prompt = ChatPromptTemplate.from_messages([
            ("system", '''You are a specialized AI assistant for web scraping. Your task is to extract structured information from the provided HTML content of a webpage.
- Analyze the HTML to find the article's title, authors, and publication date. Look in meta tags, header elements, and bylines.
- The publication date should be normalized to a 'YYYY-MM-DD' format. If you cannot find a date, leave it as null.
- For the 'text' field, extract the main article body, cleaning it of any leftover navigation, ads, or boilerplate.
- Return the data in a JSON object that matches the provided schema.'''),
            ("human", "Article URL: {url}\n\nPage HTML:\n{page_html}\n\n{format_instructions}")
        ])

        chain = prompt | llm | parser
        try:
            data = chain.invoke({
                "url": url,
                "page_html": cleaned_html[:20000],
                "format_instructions": parser.get_format_instructions()
            })
            
            if not data.get('text') or len(data.get('text', '').strip()) < 100: # Basic quality check for text
                data['text'] = body_text

            if data.get('publish_date'):
                try:
                    data['publish_date'] = parse_date(data['publish_date']).strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    print(f"[WARNING] LLM returned an invalid date format: {data['publish_date']}. Setting to None.")
                    data['publish_date'] = None
            return data
        except Exception as e:
            print(f"[ERROR] LLM failed to extract data for {url}: {e}")
            return None

    def run(self):
        """Main execution loop to scrape all configured websites based on date logic."""
        sites_config = load_json_from_supabase('website_config')
        if not sites_config:
            print("[ERROR] Website configuration not found in Supabase.")
            return

        all_new_articles = []
        for site in sites_config:
            client_name = site.get("name")
            base_url = site.get("base_url")

            if not client_name or not base_url:
                continue

            print(f"\n[INFO] --- Scraping site: {client_name} ---")

            # --- Date-based logic setup ---
            lookback_date = (datetime.now() - timedelta(days=LOOKBACK_MONTHS * 30)).date()
            last_scraped_date_str = self.scraping_state.get(client_name, {}).get("last_scraped_date")
            
            if last_scraped_date_str:
                stop_date = parse_date(last_scraped_date_str).date()
                print(f"[INFO] Resuming scan from last known date: {stop_date}")
            else:
                stop_date = lookback_date
                print(f"[INFO] First scan for this site. Looking back to {stop_date}")

            newest_article_date_this_run = None
            # --- End of date logic setup ---

            blog_index_url = self.find_blog_index_url(base_url)
            if not blog_index_url:
                potential_blog_url = urljoin(base_url, 'blog/')
                if self._get_html(potential_blog_url):
                     blog_index_url = potential_blog_url
                     print("[INFO] Found blog index via fallback: /blog/")
                else:
                    blog_index_url = base_url
                    print("[INFO] Could not find blog index, using base URL.")

            article_links = self.find_individual_article_links(blog_index_url)
            new_links = [link for link in article_links if link not in self.processed_urls]

            if not new_links:
                print("[INFO] No new article links found.")
                continue

            for link in new_links:
                article_data = self.extract_article_data(link)

                # --- Quality Gates ---
                if not article_data:
                    print(f"[SKIP] Failed to extract any data for {link}.")
                    continue
                
                if not article_data.get('publish_date'):
                    print(f"[SKIP] Article {link} has no publish date. Ignoring.")
                    continue

                if not article_data.get('text') or len(article_data.get('text', '').strip()) < 100:
                    print(f"[SKIP] Article {link} has no meaningful content. Ignoring.")
                    continue
                # --- End of Quality Gates ---

                # --- Date Comparison Logic ---
                try:
                    article_date = parse_date(article_data['publish_date']).date()
                except (ValueError, TypeError):
                    print(f"[SKIP] Could not parse date for article {link}. Ignoring.")
                    continue

                if article_date <= stop_date:
                    print(f"[INFO] Reached article with date {article_date} which is on or before stop date {stop_date}. Halting scan for this site.")
                    break
                
                # Track the newest date found in this run
                if newest_article_date_this_run is None or article_date > newest_article_date_this_run:
                    newest_article_date_this_run = article_date
                # --- End of Date Comparison ---

                article_data['client_name'] = client_name
                article_data['url'] = link
                all_new_articles.append(article_data)
                self.processed_urls.add(link)

            # Update state with the newest date from this run
            if newest_article_date_this_run:
                if client_name not in self.scraping_state:
                    self.scraping_state[client_name] = {}
                self.scraping_state[client_name]["last_scraped_date"] = newest_article_date_this_run.strftime('%Y-%m-%d')
                print(f"[INFO] Newest article for {client_name} is from {newest_article_date_this_run}. State updated.")

        if all_new_articles:
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_articles = []

            updated_articles = existing_articles + all_new_articles

            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(updated_articles, f, ensure_ascii=False, indent=2)
            print(f"\n[SUCCESS] Scraped {len(all_new_articles)} new articles. Total is now {len(updated_articles)}. Saved to {self.output_path}")
        else:
            print("\n[INFO] No new articles found across all sites.")
        
        self._save_scraping_state()


if __name__ == "__main__":
    scraper = SimpleWebsiteScraper()
    scraper.run()