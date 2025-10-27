import os
import json
from supabase import create_client

def get_supabase_client():
    """Create and return Supabase client"""
    URL = os.environ.get("SUPABASE_URL")
    KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not URL or not KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(URL, KEY)

def load_json_from_supabase(item_name: str):
    """
    Loads JSON content from a specific item in the 'items' table in Supabase.
    """
    try:
        supabase = get_supabase_client()
        res = supabase.table("items").select("payload").eq("name", item_name).single().execute()
        if res.data and "payload" in res.data:
            return res.data["payload"]
        else:
            return None
    except Exception as e:
        print(f"Error loading {item_name} from Supabase: {e}")
        return None

def get_monitored_twitter_usernames():
    """
    Get list of Twitter usernames to monitor from Supabase.
    Returns list of usernames (without @).
    """
    config = load_json_from_supabase("twitter_config")
    if not config:
        return []
    
    usernames = []
    monitored_urls = config.get("monitored_urls", [])
    
    for entry in monitored_urls:
        profile_url = entry.get("profile_url", "")
        if not profile_url:
            continue
        
        # Extract username from URL like "https://x.com/@Lica2216"
        # Handle both x.com and twitter.com
        try:
            # Get last part of URL
            username = profile_url.rstrip('/').split('/')[-1]
            # Remove @ if present
            username = username.lstrip('@')
            if username:
                usernames.append(username)
        except Exception as e:
            print(f"Failed to parse URL {profile_url}: {e}")
            continue
    
    return usernames


