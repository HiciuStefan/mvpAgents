from .email_agent import workflow  # Import the workflow
import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv


API_URL = "https://de-dashboard.vercel.app/api/agents/email"  
load_dotenv()
EMAIL_AGENT_API_KEY = os.getenv("EMAIL_AGENT_API_KEY")

headers = {
    "Content-Type": "application/json",
    "X-API-key": EMAIL_AGENT_API_KEY
}

def send_email_payload(email):
    try:
        payload = {
            "content": email.get("body", "No Body"),
            "client_name": email.get("sender"),
            "type": email.get("label","No Label"),
            "message_id": email.get("id", "No Id"),
            "subject": email.get("subject", "No Subject"),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "actionable":email.get("actionable"),
            "suggested_action": email.get("suggested_action"),
            "short_description": email.get("short_description", "No Description"),
            "relevance": email.get("relevance", "")
        }

        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        print(f"✅ Sent: {payload['subject']} – Response: {response.status_code}")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error for '{email.get('subject', 'Unknown')}': {http_err}")
    except requests.exceptions.Timeout:
        print(f"⌛ Timeout sending '{email.get('subject', 'Unknown')}'")
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection error for '{email.get('subject', 'Unknown')}'")
    except Exception as err:
        print(f"⚠️ Unexpected error for '{email.get('subject', 'Unknown')}': {err}")


def delete_payload(emails):
    try:
        response = requests.delete(API_URL, json=emails, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        print(f"✅ Deleted emails: {len(emails)} – Response: {response.status_code}")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error during delete: {http_err}")
    except requests.exceptions.Timeout:
        print(f"⌛ Timeout during delete")
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection error during delete")
    except Exception as err:
        print(f"⚠️ Unexpected error during delete: {err}")

def get_payload_for_client(client_name):
    try:
        response = requests.get(f"{API_URL}?limit=10&client_name={client_name}", headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses
        emails = response.json().get("data", [])
        print(f"✅ Fetched {len(emails)} emails for {client_name}")
        for idx, email in enumerate(emails, start=1):
            print(f"\n📧 Email #{idx}")
            print("Subject:", email.get("subject"))
            print("From:", email.get("client_name"))
            print("Date:", email.get("processed_at"))
            print("Body:", email.get("content"))
        return emails

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error during get_payload_for_client: {http_err}")
    except requests.exceptions.Timeout:
        print(f"⌛ Timeout during get_payload_for_client")
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection error during get_payload_for_client")
    except Exception as err:
        print(f"⚠️ Unexpected error during get_payload_for_client: {err}")

# Run the workflow
try:
    # result = workflow.invoke({})
    # emails = result.get("emails", [])
    get_payload_for_client("Anca Irom")
    # delete_payload(emails)
    # if not emails:
    #     print("ℹ️ No emails returned by workflow.")
    # else:
    #     for email in emails:
    #         send_email_payload(email)

except Exception as main_err:
    print(f"🚨 Failed to run workflow: {main_err}")

