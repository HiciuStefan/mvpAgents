import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")

supabase = create_client(URL, KEY)

def load_json_from_supabase(item_name: str):
    """
    Loads JSON content from a specific item in the 'items' table in Supabase.
    """
    try:
        res = supabase.table("items").select("payload").eq("name", item_name).single().execute()
        if res.data and "payload" in res.data:
            return res.data["payload"]
        else:
            print(f"No data or payload found for item: {item_name}")
            return None
    except Exception as e:
        print(f"Error loading {item_name} from Supabase: {e}")
        return None

if __name__ == "__main__":
    print("Testing load_json_from_supabase for 'user_config'...")
    user_config_data = load_json_from_supabase('user_config')

    if user_config_data:
        print("Successfully loaded 'user_config' data:")
        # Print a part of the data to confirm, avoid printing the whole large JSON
        print(f"  Company Name: {user_config_data.get('company', 'N/A')}")
        print(f"  Mission: {user_config_data.get('mission', 'N/A')}")
    else:
        print("Failed to load 'user_config' data.")

    print("\nTesting load_json_from_supabase for 'negative_scenarios'...")
    negative_scenarios_data = load_json_from_supabase('negative_scenarios')

    if negative_scenarios_data:
        print(f"Successfully loaded {len(negative_scenarios_data)} negative scenarios.")
        # Print the first item to confirm
        if negative_scenarios_data:
            print("  First negative scenario item:")
            print(negative_scenarios_data[0])
    else:
        print("Failed to load 'negative_scenarios' data.")
