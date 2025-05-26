# test_env_twitter.py

from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("TWITTER_USER1")
password = os.getenv("TWITTER_PASS1")

print("USERNAME:", username)

print("PASSWORD:", password)
