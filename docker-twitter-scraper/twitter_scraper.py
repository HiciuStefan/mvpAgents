import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service

# --- Constants ---
STATE_FILENAME = "scraping_state.json"
MAX_SCROLLS = 10 # Maximum scrolls for first scan (last 10 tweets)
MAX_SCROLLS_INCREMENTAL = 3 # Maximum scrolls for incremental scans

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)

class TwitterScraper:
    def __init__(self, headless=True):
        load_dotenv()
        self.twitter_user = os.getenv("TWITTER_USER")
        self.twitter_pass = os.getenv("TWITTER_PASS")
        
        # Verifică credențialele
        if not self.twitter_user or not self.twitter_pass:
            logging.warning("Credențialele Twitter nu sunt setate în variabilele de mediu TWITTER_USER și TWITTER_PASS")
        
        self.state_path = os.path.join(os.path.dirname(__file__), STATE_FILENAME)
        self.scraping_state = self._load_scraping_state()

        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Use manually installed FirefoxDriver
            driver_path = "/usr/local/bin/geckodriver"
            
            # Debug: print the driver path
            logging.info(f"FirefoxDriver path: {driver_path}")
            
            # Check if the driver exists and is executable
            if not os.path.exists(driver_path):
                logging.error(f"FirefoxDriver not found at: {driver_path}")
                raise Exception(f"FirefoxDriver not found at: {driver_path}")
            
            service = Service(driver_path)
            self.browser = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.browser, 10)  # Optimized timeout for speed
        except Exception as e:
            logging.error(f"Eroare la inițializarea browser-ului: {e}")
            raise

    def _load_scraping_state(self):
        """Loads the scraping state, like the last scraped tweet ID for each account."""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info(f"State file '{STATE_FILENAME}' not found. A new one will be created.")
            return {}

    def _save_scraping_state(self):
        """Saves the updated scraping state to the file."""
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.scraping_state, f, indent=2)
        logging.info(f"Scraping state saved to {self.state_path}")

    def login(self, max_retries=3):
        """Login cu retry logic și gestionare îmbunătățită a erorilor."""
        if not self.twitter_user or not self.twitter_pass:
            logging.error("Credențialele Twitter nu sunt configurate. Sări peste login.")
            return False
            
        for attempt in range(max_retries):
            try:
                logging.info(f"Încercare de conectare la Twitter (încercarea {attempt + 1}/{max_retries})...")
                self.browser.get("https://twitter.com/login")
                time.sleep(2)  # Wait for page to load - optimized
                
                # Wait for username input
                username_input = self.wait.until(EC.presence_of_element_located((By.NAME, "text")))
                username_input.clear()
                username_input.send_keys(self.twitter_user)
                username_input.send_keys(Keys.RETURN)
                time.sleep(1)  # Optimized

                # Wait for password input
                password_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
                password_input.clear()
                password_input.send_keys(self.twitter_pass)
                password_input.send_keys(Keys.RETURN)
                time.sleep(3)  # Optimized
                
                # Check if login was successful by looking for the main Twitter interface
                try:
                    self.wait.until(EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Home timeline"]'))
                    ))
                    logging.info("Conectare reușită.")
                    return True
                except TimeoutException:
                    # Check if we're on a different page (like 2FA or error page)
                    current_url = self.browser.current_url
                    if "login" not in current_url.lower():
                        logging.info("Conectare reușită (redirected away from login page).")
                        return True
                    else:
                        logging.warning(f"Conectare eșuată. URL curent: {current_url}")
                        if attempt < max_retries - 1:
                            logging.info("Reîncercare în 5 secunde...")
                            time.sleep(5)
                            continue
                        
            except TimeoutException as e:
                logging.warning(f"Timeout la conectare (încercarea {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logging.info("Reîncercare în 5 secunde...")
                    time.sleep(5)
                    continue
            except Exception as e:
                logging.error(f"Eroare neașteptată la login (încercarea {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logging.info("Reîncercare în 5 secunde...")
                    time.sleep(5)
                    continue
        
        logging.error("Conectarea la Twitter a eșuat după toate încercările.")
        return False

    def scrape_profile(self, client_name, profile_url):
        logging.info(f"Verific {client_name} -> {profile_url}")
        last_scraped_id = self.scraping_state.get(client_name, {}).get("last_scraped_tweet_id")
        
        # Determină tipul de scanare și numărul de scroll-uri
        is_first_scan = not last_scraped_id
        max_scrolls = MAX_SCROLLS if is_first_scan else MAX_SCROLLS_INCREMENTAL
        
        if is_first_scan:
            logging.info("Prima scanare pentru acest cont - caut ultimele 10 tweet-uri")
        else:
            logging.info(f"Scanare incrementală - caut tweet-uri noi după ID: {last_scraped_id}")

        self.browser.get(profile_url)
        scraped_tweets = []
        processed_in_this_run = set()
        
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']")))
            
            body = self.browser.find_element(By.TAG_NAME, "body")
            should_stop = False
            tweets_found_count = 0
            
            for i in range(max_scrolls):
                if should_stop:
                    break
                
                articles = self.browser.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
                if not articles:
                    break

                for tweet in articles:
                    try:
                        tweet_url_element = tweet.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
                        tweet_url = tweet_url_element.get_attribute("href")
                        tweet_id = tweet_url.split("/")[-1]

                        if tweet_id in processed_in_this_run:
                            continue

                        # Pentru scanarea incrementală, oprește când ajunge la ultimul tweet scanat
                        if not is_first_scan and tweet_id == last_scraped_id:
                            logging.info(f"S-a ajuns la ultimul tweet scanat ({tweet_id}). Oprire.")
                            should_stop = True
                            break
                        
                        tweet_text_element = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']")
                        tweet_text = tweet_text_element.text
                        
                        time_element = tweet.find_element(By.TAG_NAME, "time")
                        created_at = time_element.get_attribute("datetime")

                        if tweet_text and tweet_url:
                            scraped_tweets.append({
                                "client_name": client_name,
                                "tweet_id": tweet_id,
                                "text": tweet_text,
                                "url": tweet_url,
                                "created_at": created_at
                            })
                            processed_in_this_run.add(tweet_id)
                            tweets_found_count += 1

                    except NoSuchElementException:
                        continue
                
                # Pentru prima scanare, oprește după ce a găsit suficiente tweet-uri
                if is_first_scan and tweets_found_count >= 10:
                    logging.info(f"Prima scanare completă - găsite {tweets_found_count} tweet-uri. Oprire.")
                    should_stop = True
                    break
                
                logging.info(f"Scroll {i+1}/{max_scrolls}. S-au găsit {len(scraped_tweets)} tweet-uri noi până acum.")
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5) # Allow content to load - optimized for speed

        except TimeoutException:
            logging.warning(f"Timeout la încărcarea profilului {profile_url}. Poate nu există tweet-uri.")
        
        return scraped_tweets

    def save_results(self, all_tweets):
        logging.info("Salvarea rezultatelor...")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, "scraped_tweets.json")

            # Încarcă tweet-urile existente
            existing_tweets = []
            if os.path.exists(output_path):
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        existing_tweets = json.load(f)
                    logging.info(f"Încărcate {len(existing_tweets)} tweet-uri existente")
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_tweets = []

            # Creează lista de tweet-uri pentru context
            items_for_context = []
            for t in all_tweets:
                items_for_context.append({
                    "type": "twitter",
                    "client_name": t.get("client_name", "Unknown"),
                    "tweet_id": t.get("tweet_id", "0"),
                    "url": t.get("url", "https://twitter.com/unknown/status/0"),
                    "content": t.get("text", ""),
                    "created_at": t.get("created_at", datetime.now(timezone.utc).isoformat())
                })

            # Combină tweet-urile existente cu cele noi (evită duplicatele)
            existing_tweet_ids = {tweet.get("tweet_id") for tweet in existing_tweets}
            new_tweets = [tweet for tweet in items_for_context if tweet.get("tweet_id") not in existing_tweet_ids]
            
            # Adaugă tweet-urile noi la lista existentă
            combined_tweets = existing_tweets + new_tweets
            
            # Salvează lista combinată
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(combined_tweets, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Tweet-urile extrase au fost salvate în {output_path}")
            logging.info(f"Tweet-uri existente: {len(existing_tweets)}, Tweet-uri noi: {len(new_tweets)}, Total: {len(combined_tweets)}")
        except Exception as e:
            logging.error(f"A eșuat salvarea tweet-urilor: {e}")

    def run(self):
        monitored_urls = self.load_monitored_urls()
        if not monitored_urls:
            logging.warning("Nicio URL de monitorizat nu a fost găsită în configurație.")
            return []

        try:
            # Încearcă login-ul
            if not self.login():
                logging.error("Nu s-a putut conecta la Twitter. Scraping-ul nu poate continua.")
                return []

            all_tweets = []
            for profile in monitored_urls:
                client_name = profile.get("client_name")
                profile_url = profile.get("profile_url")
                if client_name and profile_url:
                    try:
                        tweets = self.scrape_profile(client_name, profile_url)
                        all_tweets.extend(tweets)
                        logging.info(f"Găsite {len(tweets)} tweet-uri noi pentru {client_name}")
                    except Exception as e:
                        logging.error(f"Eroare la scraping pentru {client_name}: {e}")
                        continue
            
            if all_tweets:
                # Update state with the newest tweet ID for each client
                newest_ids = {}
                
                # Grupează tweet-urile după client și sortează după ID pentru a găsi cel mai nou
                tweets_by_client = {}
                for tweet in all_tweets:
                    client = tweet['client_name']
                    if client not in tweets_by_client:
                        tweets_by_client[client] = []
                    tweets_by_client[client].append(tweet)
                
                # Pentru fiecare client, găsește cel mai nou tweet (după dată)
                for client, client_tweets in tweets_by_client.items():
                    # Sortează după created_at pentru a găsi cel mai nou tweet
                    sorted_tweets = sorted(client_tweets, key=lambda x: x.get('created_at', ''), reverse=True)
                    newest_tweet = sorted_tweets[0]
                    
                    # Verifică dacă tweet-ul este mai nou decât ultimul scanat
                    current_last_id = self.scraping_state.get(client, {}).get("last_scraped_tweet_id")
                    if current_last_id:
                        # Compară datele pentru a vedea dacă este mai nou
                        current_last_date = None
                        for t in client_tweets:
                            if t['tweet_id'] == current_last_id:
                                current_last_date = t.get('created_at', '')
                                break
                        
                        if current_last_date and newest_tweet.get('created_at', '') <= current_last_date:
                            logging.info(f"Pentru {client}: cel mai nou tweet ({newest_tweet['tweet_id']}) nu este mai nou decât ultimul scanat ({current_last_id}). Păstrez ultimul ID.")
                            newest_ids[client] = current_last_id
                            continue
                    
                    newest_ids[client] = newest_tweet['tweet_id']
                    logging.info(f"Pentru {client}: găsite {len(client_tweets)} tweet-uri, cel mai nou: {newest_tweet['tweet_id']} ({newest_tweet.get('created_at', 'no date')})")
                
                for client, latest_id in newest_ids.items():
                    if client not in self.scraping_state:
                        self.scraping_state[client] = {}
                    self.scraping_state[client]["last_scraped_tweet_id"] = latest_id
                    logging.info(f"Stare actualizată pentru {client}. Ultimul ID: {latest_id}")

                self.save_results(all_tweets)
                self._save_scraping_state()
                logging.info(f"Scraping finalizat. Total tweet-uri noi: {len(all_tweets)}")
            else:
                logging.info("Nu s-au găsit tweet-uri noi.")
            
            return all_tweets

        except Exception as e:
            logging.error(f"Eroare neașteptată în run(): {e}")
            return []
        finally:
            self.close()

    def load_monitored_urls(self):
        """Încarcă URL-urile monitorizate din Supabase cu fallback local."""
        logging.info("Încărcare URL-uri monitorizate din Supabase...")
        
        try:
            # Try to import supabase_retriever from current directory
            from supabase_retriever import load_json_from_supabase
            
            config = load_json_from_supabase('twitter_config')
            if config and 'monitored_urls' in config and isinstance(config['monitored_urls'], list):
                logging.info(f"Găsite {len(config['monitored_urls'])} URL-uri în configurația Supabase")
                return config['monitored_urls']
        except Exception as e:
            logging.warning(f"Eroare la încărcarea configurației din Supabase: {e}")
        
        # Fallback: încarcă din fișier local dacă există
        fallback_path = os.path.join(os.path.dirname(__file__), "twitter_config_fallback.json")
        if os.path.exists(fallback_path):
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    fallback_config = json.load(f)
                    if 'monitored_urls' in fallback_config:
                        logging.info(f"Folosesc configurația fallback cu {len(fallback_config['monitored_urls'])} URL-uri")
                        return fallback_config['monitored_urls']
            except Exception as e:
                logging.warning(f"Eroare la încărcarea configurației fallback: {e}")
        
        logging.warning("Configurația pentru Twitter nu a fost găsită în Supabase sau fișierul fallback.")
        return []

    def create_fallback_config(self, monitored_urls):
        """Creează un fișier de configurație fallback pentru testare."""
        fallback_path = os.path.join(os.path.dirname(__file__), "twitter_config_fallback.json")
        config = {
            "monitored_urls": monitored_urls,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": "Configurație fallback pentru Twitter scraper"
        }
        
        try:
            with open(fallback_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logging.info(f"Configurația fallback a fost creată în {fallback_path}")
        except Exception as e:
            logging.error(f"Eroare la crearea configurației fallback: {e}")

    def close(self):
        logging.info("Închidere browser.")
        self.browser.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter Scraper')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    parser.add_argument('--create-fallback', action='store_true', help='Create fallback config file')
    parser.add_argument('--test-urls', nargs='+', help='Test URLs for fallback config')
    
    args = parser.parse_args()
    
    # Create fallback config if requested
    if args.create_fallback and args.test_urls:
        test_urls = []
        for i, url in enumerate(args.test_urls):
            test_urls.append({
                "client_name": f"TestClient{i+1}",
                "profile_url": url
            })
        
        scraper = TwitterScraper(headless=True)
        scraper.create_fallback_config(test_urls)
        print(f"Fallback config created with {len(test_urls)} URLs")
        exit(0)
    
    # Run scraper
    scraper = TwitterScraper(headless=args.headless) 
    scraped_data = scraper.run()
    if scraped_data:
        print(f"\nScraping complete. Found {len(scraped_data)} new tweets.")
    else:
        print("\nNo new tweets found or scraping failed.")

