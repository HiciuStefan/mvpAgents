# scrape_tweets.py

import json
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Construiește calea către fișierul de configurare
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", "config", "twitter_config.json")

def load_monitored_urls():
    """Încarcă URL-urile monitorizate din fișierul JSON."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Fișierul de configurare {CONFIG_FILE} nu a fost găsit.")
        return []
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("monitored_urls", [])

load_dotenv()
TWITTER_USER = os.getenv("TWITTER_USER")
TWITTER_PASS = os.getenv("TWITTER_PASS")

def scrape_new_tweets(processed_ids: set) -> list:
    monitored_urls = load_monitored_urls()
    if not monitored_urls:
        print("Nicio URL de monitorizat nu a fost găsită în configurație.")
        return []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    browser = webdriver.Chrome(options=options)

    try:
        print("Conectare la Twitter...")
        browser.get("https://twitter.com/login")
        time.sleep(3)

        username_input = browser.find_element(By.NAME, "text")
        username_input.send_keys(TWITTER_USER)
        username_input.send_keys(Keys.RETURN)
        time.sleep(3)

        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys(TWITTER_PASS)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        all_tweets = []

        for profile in monitored_urls:
            client_name = profile["client_name"]
            profile_url = profile["profile_url"]
            print(f"Verific {client_name} -> {profile_url}")
            browser.get(profile_url)
            time.sleep(5)

            body = browser.find_element(By.TAG_NAME, "body")
            for _ in range(3):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)

            articles = browser.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")

            count = 0
            for tweet in articles:
                if count >= 3:
                    break
                try:
                    tweet_text = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']").text
                    links = tweet.find_elements(By.TAG_NAME, "a")
                    tweet_url = None
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/status/" in href:
                            tweet_url = href
                            break

                    if tweet_text and tweet_url:
                        tweet_id = tweet_url.split("/")[-1]
                        if tweet_id not in processed_ids:
                            all_tweets.append({
                                "client_name": client_name,
                                "tweet_id": tweet_id,
                                "text": tweet_text,
                                "url": tweet_url
                            })
                            count += 1
                except Exception as e:
                    print(f"⚠️ Tweet invalid: {e}")
                    continue

        return all_tweets

    finally:
        browser.quit()