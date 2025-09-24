import json
import logging
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from supabase_retriever import load_json_from_supabase

# --- Constants ---
STATE_FILENAME = "twitter_stare_scanare.json"
MAX_SCROLLS = 20 # Maximum number of scrolls to prevent infinite loops

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)

class TwitterScraper:
    def __init__(self, headless=True):
        load_dotenv()
        self.twitter_user = os.getenv("TWITTER_USER")
        self.twitter_pass = os.getenv("TWITTER_PASS")
        
        self.state_path = os.path.join(os.path.dirname(__file__), STATE_FILENAME)
        self.scraping_state = self._load_scraping_state()

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 15)

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

    def login(self):
        logging.info("Conectare la Twitter...")
        self.browser.get("https://twitter.com/login")
        try:
            username_input = self.wait.until(EC.presence_of_element_located((By.NAME, "text")))
            username_input.send_keys(self.twitter_user or "")
            username_input.send_keys(Keys.RETURN)

            password_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
            password_input.send_keys(self.twitter_pass or "")
            password_input.send_keys(Keys.RETURN)
            
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')))
            logging.info("Conectare reușită.")
        except TimeoutException:
            logging.error("Timeout la conectare. Verificati credentialele sau conexiunea.")
            self.close()
            raise

    def scrape_profile(self, client_name, profile_url):
        logging.info(f"Verific {client_name} -> {profile_url}")
        last_scraped_id = self.scraping_state.get(client_name, {}).get("last_scraped_tweet_id")
        if last_scraped_id:
            logging.info(f"Se reia scanarea de la tweet ID: {last_scraped_id}")
        else:
            logging.info("Prima scanare pentru acest cont.")

        self.browser.get(profile_url)
        scraped_tweets = []
        processed_in_this_run = set()
        
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']")))
            
            body = self.browser.find_element(By.TAG_NAME, "body")
            should_stop = False
            for i in range(MAX_SCROLLS):
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

                        if tweet_id == last_scraped_id:
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

                    except NoSuchElementException:
                        continue
                
                logging.info(f"Scroll {i+1}/{MAX_SCROLLS}. S-au găsit {len(scraped_tweets)} tweet-uri noi până acum.")
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1) # Allow content to load

        except TimeoutException:
            logging.warning(f"Timeout la încărcarea profilului {profile_url}. Poate nu există tweet-uri.")
        
        return scraped_tweets

    def save_results(self, all_tweets):
        logging.info("Salvarea rezultatelor...")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, "robust_scraped_tweets.json")

            items_for_context = []
            for t in all_tweets:
                items_for_context.append({
                    "type": "twitter",
                    "client_name": t.get("client_name", "Unknown"),
                    "tweet_id": t.get("tweet_id", "0"),
                    "url": t.get("url", "https://twitter.com/unknown/status/0"),
                    "content": t.get("text", ""),
                    "created_at": t.get("created_at", datetime.utcnow().isoformat() + "Z")
                })

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(items_for_context, f, indent=2, ensure_ascii=False)
            logging.info(f"Tweet-urile extrase au fost salvate în {output_path}")
        except Exception as e:
            logging.error(f"A eșuat salvarea tweet-urilor: {e}")

    def run(self):
        monitored_urls = self.load_monitored_urls()
        if not monitored_urls:
            logging.warning("Nicio URL de monitorizat nu a fost găsită în configurație.")
            return []

        try:
            self.login()
            all_tweets = []
            for profile in monitored_urls:
                client_name = profile.get("client_name")
                profile_url = profile.get("profile_url")
                if client_name and profile_url:
                    all_tweets.extend(self.scrape_profile(client_name, profile_url))
            
            if all_tweets:
                # Update state with the newest tweet ID for each client
                newest_ids = {}
                for tweet in all_tweets:
                    client = tweet['client_name']
                    tweet_id = int(tweet['tweet_id'])
                    if client not in newest_ids or tweet_id > newest_ids[client]:
                        newest_ids[client] = tweet_id
                
                for client, latest_id in newest_ids.items():
                    if client not in self.scraping_state:
                        self.scraping_state[client] = {}
                    self.scraping_state[client]["last_scraped_tweet_id"] = str(latest_id)
                    logging.info(f"Stare actualizată pentru {client}. Ultimul ID: {latest_id}")

                self.save_results(all_tweets)
                self._save_scraping_state()
                logging.info("Scraping finalizat.")
            else:
                logging.info("Nu s-au găsit tweet-uri noi.")
            
            return all_tweets

        finally:
            self.close()

    def load_monitored_urls(self):
        logging.info("Încărcare URL-uri monitorizate din Supabase...")
        config = load_json_from_supabase('twitter_config')
        if config and 'monitored_urls' in config and isinstance(config['monitored_urls'], list):
            return config['monitored_urls']
        logging.warning("Configurația pentru Twitter nu a fost găsită, nu conține cheia 'monitored_urls' sau aceasta nu este o listă.")
        return []

    def close(self):
        logging.info("Închidere browser.")
        self.browser.quit()

if __name__ == "__main__":
    # Set headless=False to watch the browser
    scraper = TwitterScraper(headless=True) 
    scraped_data = scraper.run()
    if scraped_data:
        # The main output is now the log. We can print a summary.
        print(f"\nScraping complete. Found {len(scraped_data)} new tweets.")
