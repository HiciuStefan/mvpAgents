import os
import json
import requests
import sys
import re
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta, date
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Add the root directory to the Python path to ensure correct module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from supabase_retriever import load_json_from_supabase
from agents._tools.llm_client import llm

# --- Constants ---
# Filename for storing the last scraped date and selectors for each website
STATE_FILENAME = "scraping_state.json"

# --- Pydantic Models for Structured Output ---



class ArticleLinks(BaseModel):
    """Pydantic model for a list of article URLs."""
    urls: List[str] = Field(description="A list of direct URLs to news or blog articles.")

class BlogIndexLinks(BaseModel):
    """Pydantic model for a list of blog index URLs."""
    urls: List[str] = Field(description="A list of URLs to main blog, news, or articles index pages.")

class PageType(str, Enum):
    BLOG_INDEX = "BLOG_INDEX"
    RESOURCES_MIX = "RESOURCES_MIX"
    SINGLE_ARTICLE = "SINGLE_ARTICLE"
    PRODUCT_PAGE = "PRODUCT_PAGE"
    OTHER = "OTHER"

class PageAnalysis(BaseModel):
    """Pydantic model for classifying a webpage."""
    page_type: PageType = Field(description="The primary type of the page.")
    reason: str = Field(description="A brief explanation for the classification.")


# --- Blog Index Processor Class ---

class BlogIndexProcessor:
    """
    A class to handle the discovery, analysis, and validation of blog index URLs.
    It manages its own state to avoid re-processing content.
    """
    def __init__(self):
        self.state_path = os.path.join(os.path.dirname(__file__), STATE_FILENAME)
        self.scraping_state = self._load_scraping_state()

    def _load_scraping_state(self) -> dict:
        """
        Loads the scraping state from a JSON file.
        """
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[INFO] State file '{STATE_FILENAME}' not found. A new one will be created.")
            return {}

    def _save_scraping_state(self):
        """
        Saves the current scraping state to its JSON file.
        """
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.scraping_state, f, indent=2)
        print(f"[INFO] Scraping state saved to {self.state_path}")

    def _get_html(self, url: str) -> Optional[str]:
        """
        Fetches the HTML content of a given URL.
        """
        try:
            if url.startswith("hhttps"):
                url = url.replace("hhttps", "https")
            response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
            return None

    def _validate_url(self, url: str) -> bool:
        """
        Validates a URL by sending a HEAD request.
        """
        try:
            if url.startswith("hhttps"):
                url = url.replace("hhttps", "https")
            response = requests.head(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True, verify=False)
            if response.status_code == 200:
                return True
            else:
                print(f"[WARN] URL validation failed for {url} with status code {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"[WARN] URL validation failed for {url}: {e}")
            return False

    def _check_for_date_in_article(self, url: str) -> bool:
        """
        Quickly checks for a date in a given article URL using regex.
        """
        print(f"[INFO] Quick checking for date in sample article: {url}")
        html_content = self._get_html(url)
        if not html_content:
            return False
        date_pattern = re.compile(
            r'(\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,\s+\d{1,2},?\s+\d{4}\b)|' # Month DD, YYYY or Mon DD, YYYY
            r'(\b\d{4}-\d{2}-\d{2}\b)' # YYYY-MM-DD
        )
        if date_pattern.search(html_content):
            print(f"[INFO] Date found in sample article {url}.")
            return True
        else:
            print(f"[INFO] No date found in sample article {url}.")
            return False

    def _analyze_page_type(self, url: str) -> Optional[PageAnalysis]:
        """
        Uses an LLM to classify the type of a given webpage.
        """
        print(f"[INFO] Analyzing page type for {url}...")
        html_content = self._get_html(url)
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        cleaned_text = str(soup.get_text(separator='\n', strip=True))

        parser = JsonOutputParser(pydantic_object=PageAnalysis)
        system_prompt = '''You are an expert web content analyst. Your task is to classify a webpage based on its content.
The possible classifications are:
- BLOG_INDEX: A page that primarily lists multiple dated news or blog articles.
- RESOURCES_MIX: A page that lists a mix of content, which might include articles, but also whitepapers, case studies, videos, or other resources.
- SINGLE_ARTICLE: A page that contains the full text of one single article.
- PRODUCT_PAGE: A page primarily describing a product or service.
- OTHER: Any other type of page (e.g., contact form, about us, main landing page).

Analyze the text content and respond with the most appropriate `page_type` and a brief `reason`.
'''
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "URL: {url}\n\nCleaned Page Text:\n{page_text}\n\n{format_instructions}")
        ])
        chain = prompt | llm | parser
        try:
            response = chain.invoke({
                "url": url,
                "page_text": cleaned_text[:15000],
                "format_instructions": parser.get_format_instructions()
            })
            return PageAnalysis(**response)
        except Exception as e:
            print(f"[ERROR] LLM analysis failed for {url}: {e}")
            return None

    def find_blog_index_urls(self, base_url: str) -> List[str]:
        """
        Finds potential blog/news index URLs from a website's base URL.
        """
        print(f"[INFO] Finding potential blog index pages on {base_url}...")
        html_content = self._get_html(base_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
        domain = urlparse(base_url).netloc
        internal_links = {link for link in all_links if urlparse(link).netloc == domain}

        keywords = ['blog', 'news', 'articles', 'insights', 'resources']
        heuristic_urls = set()
        for link in internal_links:
            for keyword in keywords:
                a_tag = soup.find('a', href=link)
                if a_tag and (keyword in link.lower() or keyword in a_tag.get_text(strip=True).lower()):
                    heuristic_urls.add(link)
                    break
        print(f"[INFO] Found {len(heuristic_urls)} potential pages with heuristics.")

        parser = JsonOutputParser(pydantic_object=BlogIndexLinks)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert web navigator. From the list of links provided, identify all URLs that are likely to be main index pages for a blog, news, or articles section. Return a JSON object containing a list of these URLs."),
            ("human", "Base URL: {base_url}\n\nLinks:\n{links}\n\n{format_instructions}")
        ])
        chain = prompt | llm | parser
        try:
            response = chain.invoke({
                "base_url": base_url,
                "links": "\n".join(sorted(list(internal_links))[:150]),
                "format_instructions": parser.get_format_instructions()
            })
            llm_urls = response.get('urls', [])
            print(f"[INFO] LLM identified {len(llm_urls)} potential pages.")
            heuristic_urls.update(llm_urls)
        except Exception as e:
            print(f"[WARN] LLM failed to find blog index pages: {e}")

        validated_urls = [url for url in heuristic_urls if self._validate_url(url)]
        print(f"[INFO] Found {len(validated_urls)} validated potential pages.")
        return validated_urls

    def find_individual_article_links(self, blog_index_url: str) -> List[str]:
        """
        Finds and lists all direct article links from a news/blog index page.
        """
        print(f"[INFO] Finding individual article links on {blog_index_url}...")
        html_content = self._get_html(blog_index_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = [urljoin(blog_index_url, a['href']) for a in soup.find_all('a', href=True)]
        domain = urlparse(blog_index_url).netloc
        internal_links = {link for link in all_links if urlparse(link).netloc == domain}

        heuristic_urls = set()
        for link in internal_links:
            if len(urlparse(link).path.split('/')) > 2:
                heuristic_urls.add(link)
        print(f"[INFO] Found {len(heuristic_urls)} potential article links with heuristics.")

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
            llm_urls = response.get('urls', [])
            print(f"[INFO] LLM identified {len(llm_urls)} potential article links.")
            heuristic_urls.update(llm_urls)
        except Exception as e:
            print(f"[WARN] LLM failed to extract individual article links: {e}")

        validated_urls = [url for url in heuristic_urls if self._validate_url(url)]
        print(f"[INFO] Found {len(validated_urls)} validated article links.")
        return validated_urls

    def process_blog_indexes(self, base_url: str, client_name: str) -> None:
        """
        Discovers, analyzes, and validates blog index URLs for a given client.
        Updates the internal scraping_state dictionary with accepted and rejected URLs.
        """
        if client_name not in self.scraping_state:
            self.scraping_state[client_name] = {}
        
        self.scraping_state[client_name].setdefault("blog_index_urls", [])
        self.scraping_state[client_name].setdefault("rejected_index_urls", [])

        if not self.scraping_state[client_name]["blog_index_urls"]:
            print(f"[INFO] No cached blog index URLs found for {client_name}. Searching and validating...")
            
            potential_urls = self.find_blog_index_urls(base_url)

            if potential_urls:
                for url in potential_urls:
                    if url in self.scraping_state[client_name]["blog_index_urls"] or url in self.scraping_state[client_name]["rejected_index_urls"]:
                        continue
                    
                    analysis = self._analyze_page_type(url)
                    if not analysis:
                        print(f"[WARN] Could not analyze page type for {url}. Rejecting.")
                        self.scraping_state[client_name]["rejected_index_urls"].append(url)
                        continue

                    if analysis.page_type == PageType.BLOG_INDEX:
                        print(f"[ACCEPT] Accepted {url} as a blog index. Reason: {analysis.reason}")
                        self.scraping_state[client_name]["blog_index_urls"].append(url)
                    elif analysis.page_type == PageType.RESOURCES_MIX:
                        print(f"[INFO] Page {url} is a mix of resources. Checking for dates in sample articles...")
                        sample_articles = self.find_individual_article_links(url)
                        if sample_articles and self._check_for_date_in_article(sample_articles[0]):
                            print(f"[ACCEPT] Accepted resource page {url} because its articles have dates.")
                            self.scraping_state[client_name]["blog_index_urls"].append(url)
                        else:
                            print(f"[REJECT] Rejected resource page {url} because its articles seem to lack dates.")
                            self.scraping_state[client_name]["rejected_index_urls"].append(url)
                    else:
                        print(f"[REJECT] Rejected {url}. Type: {analysis.page_type}. Reason: {analysis.reason}")
                        self.scraping_state[client_name]["rejected_index_urls"].append(url)
                
                self._save_scraping_state()
            else:
                print("[INFO] No potential blog index URLs found. Skipping site.")

if __name__ == "__main__":
    print("--- Starting BlogIndexProcessor Direct Run ---")
    processor = BlogIndexProcessor()

    sites_config = load_json_from_supabase('website_config')
    if not sites_config:
        print("[ERROR] Website configuration not found in Supabase. Exiting.")
    else:
        for site in sites_config:
            client_name = site.get("name")
            base_url = site.get("base_url")

            if not client_name or not base_url:
                continue

            print(f"\nProcessing site: {client_name} ({base_url})")
            processor.process_blog_indexes(base_url, client_name)

            print("\nUpdated Scraping State for this site:")
            print(json.dumps(processor.scraping_state, indent=2))

    print("\n--- BlogIndexProcessor Direct Run Complete ---")
