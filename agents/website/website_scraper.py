import os
import json
import newspaper
import sys
import requests
import re
from bs4 import BeautifulSoup, Comment
from dateutil.parser import parse as parse_date
from langchain_core.prompts import ChatPromptTemplate
from urllib.parse import urljoin

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from supabase_retriever import load_json_from_supabase
from agents._tools.llm_client import llm

class WebsiteScraper:
    CLIENT_CONFIG = {
        "UIPath": {
            "date_meta_properties": [
                "article:published_time",
                "date",
                "og:pubdate",
                "citation_date",
                "dc.date",
                "pubdate"
            ],
            "date_selectors": [
                "span.BlogPost__Byline-Date",
                "time[datetime]"
            ]
        }
    }

    def __init__(self):
        self.processed_urls = set()
        self.selector_cache = {}
        self.last_scraped_date_cache = {}

    def load_sites_config(self):
        """Loads website configurations from Supabase (item 'website_config')."""
        config = load_json_from_supabase('website_config')
        if config:
            return config
        print("Website configuration not found in Supabase.")
        return []

    def get_date_selector_with_llm(self, url):
        """Gets a CSS selector for the publication date using an LLM."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = str(soup.prettify())

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at analyzing HTML and finding CSS selectors. Your task is to find the most reliable and specific CSS selector for the publication date of an article. Return only the CSS selector and nothing else."),
                ("human", "Here is the HTML of the article:\n\n{html}")
            ])
            
            chain = prompt | llm
            response = chain.invoke({"html": html_content})
            selector = response.content.strip()
            print(f"[DEBUG] LLM identified date selector: {selector}")
            return selector
        except Exception as e:
            print(f"[DEBUG] Could not get date selector with LLM: {e}")
            return None

    def find_blog_or_news_links(self, base_url):
        """Finds links to blog or news pages using an LLM."""
        try:
            response = requests.get(base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                if link.startswith('http'):
                    links.append(link)
                else:
                    links.append(urljoin(base_url, link))
            
            if not links:
                return []

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at identifying blog or news page URLs. From the following list of URLs, please identify the ones that are most likely to be main blog or news pages. Return a comma-separated list of the URLs."),
                ("human", "{links}")
            ])
            
            chain = prompt | llm
            response = chain.invoke({"links": '\n'.join(links)})
            blog_links = [link.strip() for link in response.content.split(',')]
            print(f"[DEBUG] LLM identified blog/news links: {blog_links}")
            return blog_links
        except Exception as e:
            print(f"[DEBUG] Could not find blog/news links with LLM: {e}")
            return []

    def scrape_article_links(self, url):
        """Scrapes article links from a given URL using newspaper3k."""
        try:
            paper = newspaper.build(url, memoize_articles=False)
            return [article.url for article in paper.articles]
        except Exception as e:
            print(f"Error building paper for {url}: {e}")
            return []

    def extract_date_with_llm(self, text):
        """Extracts the publication date from text using an LLM."""
        if not text:
            return None
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at finding the publication date in an article. Your task is to extract the publication date from the given text. Return only the date in YYYY-MM-DD format and nothing else."),
            ("human", "{text}")
        ])
        
        chain = prompt | llm
        try:
            response = chain.invoke({"text": text})
            date_str = response.content.strip()
            print(f"[DEBUG] LLM extracted date: {date_str}")
            return parse_date(date_str)
        except Exception as e:
            print(f"[DEBUG] Could not extract date with LLM: {e}")
            return None

    def scrape_article_content(self, url, site_config):
        """Scrapes content from a single article URL."""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()

            publish_date = article.publish_date
            print(f"[DEBUG] Initial publish_date for {url}: {publish_date}")
            client_name = site_config.get("name")

            # Fallback for publish_date
            if not publish_date:
                print(f"[DEBUG] publish_date is None, trying fallback for {url}")
                try:
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Try with cached or new selector
                    if client_name in self.selector_cache:
                        selector = self.selector_cache[client_name]
                        print(f"[DEBUG] Using cached selector for {client_name}: {selector}")
                        date_element = soup.select_one(selector)
                        if date_element:
                            date_text = date_element.get_text(strip=True)
                            print(f"[DEBUG] Found date with cached selector: {date_text}")
                            publish_date = parse_date(date_text)
                    else:
                        print(f"[DEBUG] No selector in cache for {client_name}, getting one with LLM.")
                        selector = self.get_date_selector_with_llm(url)
                        if selector:
                            self.selector_cache[client_name] = selector
                            date_element = soup.select_one(selector)
                            if date_element:
                                date_text = date_element.get_text(strip=True)
                                print(f"[DEBUG] Found date with new selector: {date_text}")
                                publish_date = parse_date(date_text)

                    if not publish_date:
                        if client_name == "Opaque":
                            print(f"[DEBUG] Running Opaque logic for {url}")
                            script_tag = soup.find("script", {"type": "application/ld+json"})
                            if script_tag:
                                try:
                                    json_data = json.loads(script_tag.string)
                                    if 'datePublished' in json_data:
                                        date_str = json_data['datePublished']
                                        print(f"[DEBUG] Found datePublished for Opaque from ld+json: {date_str}")
                                        publish_date = parse_date(date_str)
                                except json.JSONDecodeError:
                                    print(f"[DEBUG] Could not decode JSON from script tag for Opaque url: {url}")
                            
                            if not publish_date:
                                # Try to extract date from HTML comments
                                comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                                for comment in comments:
                                    if "Last Published:" in comment:
                                        match = re.search(r'Last Published: (.*? GMT)', comment)
                                        if match:
                                            date_str = match.group(1).strip()
                                            print(f"[DEBUG] Found date from HTML comment for Opaque: {date_str}")
                                            publish_date = parse_date(date_str)
                                            break
                                if not publish_date:
                                    # Try to extract date from URL for Opaque
                                    match = re.search(r'\/(\d{4})\/(\d{2})\/(\d{2})\/', url)
                                    if match:
                                        date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                                        print(f"[DEBUG] Found date from URL for Opaque: {date_str}")
                                        publish_date = parse_date(date_str)
                                    else:
                                        print(f"[DEBUG] No date found in URL for Opaque url: {url}")

                        elif client_name in self.CLIENT_CONFIG:
                            print(f"[DEBUG] Running UIPath logic for {url}")
                            # Try meta properties first
                            if "date_meta_properties" in self.CLIENT_CONFIG[client_name]:
                                for prop in self.CLIENT_CONFIG[client_name]["date_meta_properties"]:
                                    meta_tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
                                    if meta_tag and meta_tag.get("content"):
                                        date_str = meta_tag.get("content")
                                        print(f"[DEBUG] Found date from meta property {prop} for UIPath: {date_str}")
                                        publish_date = parse_date(date_str)
                                        break
                            
                            # If not found, try CSS selectors
                            if not publish_date and "date_selectors" in self.CLIENT_CONFIG[client_name]:
                                for selector in self.CLIENT_CONFIG[client_name]["date_selectors"]:
                                    date_element = soup.select_one(selector)
                                    if date_element:
                                        date_text = date_element.get_text(strip=True)
                                        print(f"[DEBUG] Found date from CSS selector {selector} for UIPath: {date_text}")
                                        publish_date = parse_date(date_text)
                                        break
                except Exception as e:
                    print(f"Could not extract date for {url} with custom logic: {e}")
            
            # Fallback: try to extract date from article text using regex
            if not publish_date and article.text:
                print(f"[DEBUG] Trying regex fallback for date in article text for {url}")
                # Common date patterns: YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY
                date_patterns = [
                    r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                    r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY or M/D/YYYY
                    r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b', # Month DD, YYYY
                    r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b' # DD Month YYYY
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, article.text)
                    if match:
                        date_str = match.group(0)
                        try:
                            publish_date = parse_date(date_str)
                            print(f"[DEBUG] Found date from regex in article text: {date_str}")
                            break
                        except ValueError:
                            print(f"[DEBUG] Could not parse date from regex match: {date_str}")

            # Final fallback: use LLM to extract date
            if not publish_date and article.text:
                print(f"[DEBUG] Trying LLM fallback for date in article text for {url}")
                publish_date = self.extract_date_with_llm(article.text)

            print(f"[DEBUG] Final publish_date for {url}: {publish_date}")

            if not publish_date:
                print(f"[INFO] Ignoring article without a date: {url}")
                return None

            last_scraped_date = self.last_scraped_date_cache.get(client_name)
            if last_scraped_date and publish_date.replace(tzinfo=None) <= last_scraped_date.replace(tzinfo=None):
                print(f"[INFO] Ignoring old article: {url} ({publish_date})")
                return None

            self.last_scraped_date_cache[client_name] = publish_date

            return {
                "title": article.title,
                "authors": article.authors,
                "publish_date": publish_date.isoformat() if publish_date else None,
                "text": article.text,
                "url": url
            }
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None

    def run(self, limit=10):
        sites_config = self.load_sites_config()
        all_articles = []

        # In a real application, you would load this from a persistent store
        self.last_scraped_date_cache = {}

        for site in sites_config:
            client_name = site.get("name")
            base_url = site.get("base_url")

            if not client_name or not base_url:
                continue

            # Correct the typo in the Opaque URL
            if client_name == "Opaque" and base_url.startswith("hhttps"):
                base_url = base_url.replace("hhttps", "https")

            print(f"Scraping site: {client_name}")
            
            blog_links = self.find_blog_or_news_links(base_url)
            if not blog_links:
                print(f"  - No blog/news links found with LLM, falling back to scraping all links from: {base_url}")
                blog_links = [base_url]

            articles_scraped_for_site = 0
            for blog_link in blog_links:
                if articles_scraped_for_site >= limit:
                    break

                print(f"  - Scraping index page: {blog_link}")
                links = self.scrape_article_links(blog_link)
                print(f"    - Found {len(links)} article links.")
                
                for link in links:
                    if articles_scraped_for_site >= limit:
                        break
                    if link not in self.processed_urls:
                        content = self.scrape_article_content(link, site)
                        if content:
                            content["client_name"] = client_name
                            all_articles.append(content)
                            self.processed_urls.add(link)
                            articles_scraped_for_site += 1

        return all_articles

if __name__ == "__main__":
    scraper = WebsiteScraper()
    articles = scraper.run(limit=5)
    if articles:
        # Define the output path
        output_dir = os.path.dirname(__file__)
        output_path = os.path.join(output_dir, "scraped_articles.json")
        
        # Save results to a file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\nScraped articles saved to {output_path}")
    else:
        print("\nNo new articles found.")




