import os
import json
import sys
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin, urlparse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from typing import Tuple, List, Dict, Any
from xml.etree import ElementTree

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from llm_client import llm

KEYWORDS = [
    'blog', 'news', 'articles', 'insights', 'resources', 'stories', 'press', 'events', 'updates', 'journal', 'media', 'publications'
]
EXCLUDE_KEYWORDS = [
    'contact', 'about', 'login', 'register', 'privacy', 'terms', 'careers', 'support', 'faq', 'cookies', 'cart', 'account'
]
EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.mp4', '.avi', '.mov')

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# Căi comune pentru pagini index de conținut (fallback când homepage-ul nu are link direct)
COMMON_INDEX_PATHS = [
    "/blog",
    "/community-blog",
    "/resources",
    "/insights",
    "/newsroom",
    "/news",
    "/press",
    "/stories",
    "/updates",
    "/articles",
]

# Tokenuri acceptate pentru secțiuni index (generice, fără hardcoding pe domenii)
INDEX_TOKENS = {"blog", "community-blog", "resources", "insights", "news", "press", "stories", "updates", "articles", "c"}

# Reguli specifice pe domeniu pentru a exclude anumite căi ca indexuri
DOMAIN_EXCLUDE_INDEX_SEGMENTS = {
    "uipath.com": {"/events", "/resources"}
}

# Limită de candidați pentru validare/LLM, pentru a accelera rularile
MAX_INDEX_CANDIDATES = 80

# Acceptă doar locale en/ro; excludem alte prefixe de limbă
ALLOWED_LOCALES = {"en", "ro"}
LOCALE_REGEX = re.compile(r"^/([a-z]{2})(/|$)")

LLM_PROMPT = """
You are a web content analyst. Classify a web page based on its cleaned text content.
Possible classifications:
- BLOG_INDEX: Lists multiple dated news/blog articles (titles/excerpts, pagination, categories). Not a single post.
- RESOURCES_MIX: A hub that mixes articles with whitepapers/case studies/videos.
- SINGLE_ARTICLE: The full content of one article/post.
- PRODUCT_PAGE: Describes a product/service.
- OTHER: Anything else (contact/about/landing/pricing/etc.).

Rules:
- Prefer BLOG_INDEX only for section root pages (e.g., /blog, /community-blog, /resources), not individual articles.
- If unsure between BLOG_INDEX and RESOURCES_MIX, pick RESOURCES_MIX.
- Keep the answer short and objective.

Return ONLY JSON with: {{"page_type": "...", "reason": "..."}}
"""

class PageAnalysis(BaseModel):
    page_type: str = Field(description="Type of the page")
    reason: str = Field(description="Short reason for classification")

class BlogIndexLinks(BaseModel):
    urls: List[str] = Field(description="A list of URLs to main blog/news/resources index pages")

class BlogIndexProcessor:
    def __init__(self):
        self.output_parser = JsonOutputParser(pydantic_object=PageAnalysis)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", LLM_PROMPT),
            ("human", "{text}")
        ])
        self.index_list_parser = JsonOutputParser(pydantic_object=BlogIndexLinks)
        self.index_list_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert web navigator. Given a site's base URL and a list of internal links (with anchor text), return only the root section URLs that likely serve as indexes for blog/news/resources articles. Output JSON with 'urls'."),
            ("human", "Base URL: {base_url}\n\nLinks (text -> url):\n{links}\n\n{format}")
        ])

    def _canonicalize_url(self, url: str) -> str:
        try:
            parts = urlparse(url)
            scheme = parts.scheme.lower()
            netloc = parts.netloc.lower()
            path = parts.path.rstrip('/') or '/'
            return f"{scheme}://{netloc}{path}"
        except Exception:
            return url

    def _strip_locale_from_path(self, path: str) -> List[str]:
        # returnează segmentele fără prefix de limbă (en/ro/etc.)
        segs = [s for s in path.split('/') if s]
        if segs and len(segs[0]) == 2 and segs[0].isalpha():
            return segs[1:]
        return segs

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
        # Accept same domain or subdomains
        return cand_netloc == base_netloc or cand_netloc.endswith("." + base_netloc)

    def _get_html(self, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

    def _discover_from_sitemap(self, base_url: str) -> List[str]:
        candidates: List[str] = []
        parsed = urlparse(base_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        for path in ("/sitemap.xml", "/sitemap_index.xml"):
            sitemap_url = urljoin(root, path)
            try:
                resp = requests.get(sitemap_url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True)
                if resp.status_code != 200:
                    continue
                content = resp.text
                # Simplu: căutăm URL-uri în sitemap care conțin cuvinte cheie
                try:
                    tree = ElementTree.fromstring(content)
                    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    loc_elems = tree.findall('.//sm:loc', ns)
                    if not loc_elems:
                        loc_elems = tree.findall('.//loc')
                    for loc in loc_elems:
                        url_text = loc.text or ""
                        path = urlparse(url_text).path
                        segs = self._strip_locale_from_path(path)
                        # Acceptă secțiuni cu un segment (ex: /blog) sau pattern /c/category-name
                        if (len(segs) == 1 and segs[0].lower() in INDEX_TOKENS) or \
                           (len(segs) == 2 and segs[0].lower() == "c"):
                            candidates.append(url_text)
                except ElementTree.ParseError:
                    # Fallback simplu pe regex
                    for m in re.finditer(r"<loc>(.*?)</loc>", content, re.IGNORECASE):
                        url_text = m.group(1)
                        path = urlparse(url_text).path
                        segs = self._strip_locale_from_path(path)
                        # Acceptă secțiuni cu un segment (ex: /blog) sau pattern /c/category-name
                        if (len(segs) == 1 and segs[0].lower() in INDEX_TOKENS) or \
                           (len(segs) == 2 and segs[0].lower() == "c"):
                            candidates.append(url_text)
            except Exception:
                continue
        return list(set(candidates))

    def _discover_rss_feeds(self, base_url: str) -> List[str]:
        parsed = urlparse(base_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        common = [
            "/feed", "/rss", "/rss.xml"
        ] + [f"/{token}/feed" for token in INDEX_TOKENS] + [f"/{token}/rss" for token in INDEX_TOKENS]
        feeds = []
        for p in common:
            u = urljoin(root, p)
            try:
                r = requests.head(u, timeout=5, headers=REQUEST_HEADERS, allow_redirects=True)
                if 200 <= r.status_code < 400:
                    # Păstrează doar feed-uri de secțiune (rădăcină sau 1 segment + feed)
                    segs = self._strip_locale_from_path(urlparse(u).path)
                    base_segs = [s for s in segs if s not in ("feed", "rss", "rss.xml")]
                    if len(base_segs) == 1 and base_segs[0].lower() in INDEX_TOKENS:
                        feeds.append(u)
            except Exception:
                continue
        return list(set(feeds))

    def _validate_url(self, url: str) -> bool:
        try:
            resp = requests.head(url, timeout=7, headers=REQUEST_HEADERS, allow_redirects=True)
            if 200 <= resp.status_code < 400:
                return True
            # Fallback to GET for servers that don't support HEAD or block it
            if resp.status_code in (405, 403):
                resp_get = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True, stream=True)
                return 200 <= resp_get.status_code < 400
            return False
        except Exception:
            try:
                resp_get = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True, stream=True)
                return 200 <= resp_get.status_code < 400
            except Exception:
                return False

    def _analyze_page_type(self, url: str) -> dict:
        html = self._get_html(url)
        if not html:
            return {"page_type": "OTHER", "reason": "empty_or_fetch_error"}
        soup = BeautifulSoup(html, "html.parser")
        # Curățare: scoate elemente de navigație/cod pentru un semnal mai bun
        for tag_name in ("script", "style", "nav", "footer", "header", "aside", "form"):
            for el in soup.find_all(tag_name):
                el.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = text[:15000]
        try:
            chain = self.prompt | llm | self.output_parser
            result = chain.invoke({"text": text})
            page_type = result.get("page_type", "OTHER") if isinstance(result, dict) else "OTHER"
            reason = result.get("reason", "no_reason") if isinstance(result, dict) else "no_reason"
            return {"page_type": page_type, "reason": reason}
        except Exception as e:
            print(f"[ERROR] LLM analysis failed for {url}: {e}")
            return {"page_type": "OTHER", "reason": "llm_error"}

    def _resolve_final_url(self, url: str) -> str | None:
        try:
            resp = requests.head(url, timeout=7, headers=REQUEST_HEADERS, allow_redirects=True)
            if 200 <= resp.status_code < 400:
                return resp.url
            if resp.status_code in (405, 403):
                resp_get = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True, stream=True)
                if 200 <= resp_get.status_code < 400:
                    return resp_get.url
            return None
        except Exception:
            try:
                resp_get = requests.get(url, timeout=10, headers=REQUEST_HEADERS, allow_redirects=True, stream=True)
                if 200 <= resp_get.status_code < 400:
                    return resp_get.url
                return None
            except Exception:
                return None

    def find_blog_index_urls(self, base_url: str) -> Tuple[List[str], List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
        html = self._get_html(base_url)
        soup = BeautifulSoup(html, "html.parser")
        heuristic_urls_set = set()
        priority_candidates: List[str] = []
        other_candidates: List[str] = []
        link_entries: List[str] = []
        # Construiește mapare anchor -> url absolut și filtrează scheme non-HTTP
        for a in soup.find_all("a", href=True):
            if not isinstance(a, Tag):
                continue
            href_attr = a.attrs.get("href", "")
            href = href_attr.strip() if isinstance(href_attr, str) else str(href_attr)
            if not self._is_http_url(href):
                continue
            abs_url = urljoin(base_url, href)
            # Exclude locale neacceptate (păstrează root fără prefix)
            path_only = urlparse(abs_url).path
            m = LOCALE_REGEX.match(path_only)
            if m and m.group(1) not in ALLOWED_LOCALES:
                continue
            if not self._is_internal(base_url, abs_url):
                continue
            # Exclude fișiere binare / media
            if abs_url.lower().endswith(EXTENSIONS):
                continue
            # Exclude după cuvinte cheie evidente
            if any(x in abs_url.lower() for x in EXCLUDE_KEYWORDS):
                continue
            anchor_text = a.get_text(strip=True).lower()
            if len(link_entries) < 200:
                link_entries.append(f"{anchor_text or '-'} -> {abs_url}")
            for keyword in KEYWORDS:
                if keyword in abs_url.lower() or keyword in anchor_text:
                    path = urlparse(abs_url).path
                    segs = self._strip_locale_from_path(path)
                    # Acceptă strict pagini index (rădăcină sau 1 segment din INDEX_TOKENS) sau pattern /c/category-name
                    if (len(segs) == 1 and segs[0].lower() in INDEX_TOKENS) or \
                       (len(segs) == 2 and segs[0].lower() == "c"):
                        if abs_url not in heuristic_urls_set:
                            heuristic_urls_set.add(abs_url)
                            if 'blog' in abs_url.lower():
                                priority_candidates.append(abs_url)
                            else:
                                other_candidates.append(abs_url)
                    break

        # LLM selecție inițială pe lista de linkuri din homepage
        try:
            if link_entries:
                chain = self.index_list_prompt | llm | self.index_list_parser
                llm_sel = chain.invoke({
                    "base_url": base_url,
                    "links": "\n".join(link_entries),
                    "format": self.index_list_parser.get_format_instructions(),
                })
                llm_urls = llm_sel.get("urls", []) if isinstance(llm_sel, dict) else []
                for u in llm_urls:
                    u_abs = urljoin(base_url, u)
                    path = urlparse(u_abs).path
                    segs = self._strip_locale_from_path(path)
                    # Acceptă secțiuni cu un segment (ex: /blog) sau pattern /c/category-name
                    if (len(segs) == 1 and segs[0].lower() in INDEX_TOKENS) or \
                       (len(segs) == 2 and segs[0].lower() == "c"):
                        if u_abs not in heuristic_urls_set:
                            heuristic_urls_set.add(u_abs)
                            if 'blog' in u_abs.lower():
                                priority_candidates.append(u_abs)
                            else:
                                other_candidates.append(u_abs)
        except Exception as e:
            print(f"[WARN] LLM list selection failed: {e}")
        # Simplificat: nu mai adăugăm candidați din sitemap/RSS – doar linkurile din homepage

        # Fallback: încearcă căi comune direct pe domeniu (prioritar)
        parsed_base = urlparse(base_url)
        base_root = f"{parsed_base.scheme}://{parsed_base.netloc}"
        for path in COMMON_INDEX_PATHS:
            candidate = urljoin(base_root, path)
            if any(x in candidate.lower() for x in EXCLUDE_KEYWORDS):
                continue
            if candidate.lower().endswith(EXTENSIONS):
                continue
            m = LOCALE_REGEX.match(urlparse(candidate).path)
            if m and m.group(1) not in ALLOWED_LOCALES:
                continue
            if candidate not in heuristic_urls_set:
                heuristic_urls_set.add(candidate)
                priority_candidates.append(candidate)

        # Construieste lista finală păstrând prioritatea și ordinea de inserție
        heuristic_urls_ordered: List[str] = []
        for u in priority_candidates + other_candidates:
            if u not in heuristic_urls_ordered:
                heuristic_urls_ordered.append(u)
        
        # Taie candidații pentru un mod mai rapid
        if len(heuristic_urls_ordered) > MAX_INDEX_CANDIDATES:
            heuristic_urls_ordered = heuristic_urls_ordered[:MAX_INDEX_CANDIDATES]
        print(f"[INFO] Validating {len(heuristic_urls_ordered)} candidate index URLs... (priority first)")
        # Validare și clasificare cu LLM
        blog_index_urls = []
        rejected_index_urls = []
        accepted_details = []
        rejected_details = []
        for i, url in enumerate(heuristic_urls_ordered, start=1):
            if i % 10 == 0:
                print(f"[INFO] Processed {i}/{len(heuristic_urls_ordered)} candidates...")
            # Excluderi specifice de domeniu pentru a evita secțiuni non-blog la clienți cunoscuți
            parsed = urlparse(url)
            netloc = self._normalize_netloc(parsed.netloc)
            domain_key = netloc.split(":")[0]
            # Filtru generic de limbă (acceptă doar en/ro dacă există prefix de limbă)
            first_seg = next((s for s in parsed.path.split('/') if s), "")
            if len(first_seg) == 2 and first_seg.isalpha() and first_seg.lower() not in ALLOWED_LOCALES:
                continue
            for rule_domain, excluded_paths in DOMAIN_EXCLUDE_INDEX_SEGMENTS.items():
                if domain_key.endswith(rule_domain):
                    for ex_path in excluded_paths:
                        if parsed.path.startswith(ex_path):
                            # Sare peste acest URL ca index
                            rejected_index_urls.append(url)
                            rejected_details.append({"url": url, "analysis": {"page_type": "OTHER", "reason": "domain_rule_excluded"}})
                            url = None
                            break
                if url is None:
                    break
            if url is None:
                continue
            final_url = self._resolve_final_url(url)
            if not final_url:
                continue
            analysis = self._analyze_page_type(final_url)
            if analysis.get("page_type") in ("BLOG_INDEX", "RESOURCES_MIX"):
                canon = self._canonicalize_url(final_url)
                if canon not in {self._canonicalize_url(u) for u in blog_index_urls}:
                    blog_index_urls.append(final_url)
                accepted_details.append({"url": canon, "analysis": analysis})
            else:
                if url not in rejected_index_urls:
                    rejected_index_urls.append(url)
                rejected_details.append({"url": url, "analysis": analysis})
        # Deduplicate final list strictly by canonical form
        seen = set()
        deduped = []
        for u in blog_index_urls:
            cu = self._canonicalize_url(u)
            if cu in seen:
                continue
            seen.add(cu)
            deduped.append(u)
        return deduped, rejected_index_urls, accepted_details, rejected_details

    def process_website(self, base_url: str, client_name: str, scraping_state: dict):
        client_key = f"{client_name}|{base_url}"
        blog_index_urls, rejected_index_urls, accepted_details, rejected_details = self.find_blog_index_urls(base_url)
        # Replace with canonicalized unique URLs and drop any old duplicates in state
        scraping_state[client_key] = {
            "blog_index_urls": [self._canonicalize_url(u) for u in blog_index_urls],
            "rejected_index_urls": rejected_index_urls,
            # Noi câmpuri cu detalii pentru observabilitate
            "blog_index_details": accepted_details,
            "rejected_index_details": rejected_details
        }
        print(f"[INFO] Selected {len(blog_index_urls)} blog index URLs for {client_key}")

    def get_scraping_state_path():
        if os.environ.get("WEBSITE_INSTANCE_ID"):
            # Running in Azure Functions → use /tmp
            return os.path.join("/tmp", "scraping_state.json")
        else:
            # Running locally → save next to script
            return os.path.join(os.path.dirname(__file__), "scraping_state.json")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python blog_index_processor.py [base_url] [client_name]")
        sys.exit(1)
    base_url = sys.argv[1]
    client_name = sys.argv[2]
    scraping_state_path = BlogIndexProcessor.get_scraping_state_path()
    try:
        with open(scraping_state_path, "r", encoding="utf-8") as f:
            scraping_state = json.load(f)
    except Exception:
        scraping_state = {}
    processor = BlogIndexProcessor()
    processor.process_website(base_url, client_name, scraping_state)
    with open(scraping_state_path, "w", encoding="utf-8") as f:
        json.dump(scraping_state, f, indent=2, ensure_ascii=False)