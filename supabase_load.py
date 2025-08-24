import os, json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase = create_client(URL, KEY)

def insert_item(name: str, file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)   # citește fișierul .json
    res = supabase.table("items").insert({"name": name, "payload": payload}).execute()
    print("Inserted:", res.data)

# exemplu de apel
insert_item("negative_scenarios", "C:\\Users\\vasil\\Desktop\\mvpAgents\\context\\scenarios\\negative_scenarios.json")
insert_item("neutral_scenarios", "C:\\Users\\vasil\\Desktop\\mvpAgents\\context\\scenarios\\neutral_scenarios.json")
insert_item("positive_scenarios", "C:\\Users\\vasil\\Desktop\\mvpAgents\\context\\scenarios\\positive_scenarios.json")
insert_item("twitter_scraped", "C:\\Users\\vasil\\Desktop\\mvpAgents\\context\\scenarios\\twitter_scraped.json")