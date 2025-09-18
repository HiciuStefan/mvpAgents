
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from .enhance_and_filter_emails_workflow import enhance_and_filter_emails_workflow,AgentState
from flask import Flask, request, jsonify

app = Flask(__name__)

load_dotenv()
EMAIL_AGENT_URL =  os.getenv("EMAIL_AGENT_URL")  
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
            "relevance": email.get("relevance", ""),
            "suggested_reply": email.get("suggested_reply", "")
        }

        if EMAIL_AGENT_URL is None:
            raise ValueError("EMAIL_AGENT_URL environment variable is not set.")

        response = requests.post(EMAIL_AGENT_URL, json=payload, headers=headers, timeout=10)
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
        if EMAIL_AGENT_URL is None:
            raise ValueError("EMAIL_AGENT_URL environment variable is not set.")
        response = requests.delete(EMAIL_AGENT_URL, json=emails, headers=headers, timeout=10)
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
        if EMAIL_AGENT_URL is None:
            raise ValueError("EMAIL_AGENT_URL environment variable is not set.")
        
        response = requests.get(f"{EMAIL_AGENT_URL}?limit=10&client_name={client_name}", headers=headers, timeout=10)
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

def send_to_server(data):
    url = "http://127.0.0.1:5000/normal"  # change to your server's address
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # will raise an error if not 2xx
        return response.json()       # parse JSON reply
    except requests.RequestException as e:
        print(f"Error sending data to server: {e}")
        return None
        
@app.route("/normal", methods=["GET"])
def handle_data_normal():
    # Run the workflow
    try:
        result = enhance_and_filter_emails_workflow.invoke(AgentState(emails=[], filtered_emails=[], email_creds=None))
        emails = result.get("emails", [])

        if not emails:
            print("ℹ️ No emails returned by workflow.")
            return jsonify({"message": "No emails returned by workflow.", "emails": []}), 200
        else:
            filtered_emails = [
        {k: v for k, v in email.items() if k != "body"}
        for email in emails
    ]
            for email in emails:
                send_email_payload(email)
            return jsonify({"message": "Emails processed and sent.", "emails": filtered_emails}), 200
        # return jsonify({"message": "Workflow execution is currently disabled."}), 200

    except Exception as main_err:
        print(f"🚨 Failed to run workflow: {main_err}")
        return jsonify({"error": str(main_err)}), 500

@app.route("/paramRoute", methods=["GET"])
def handle_data__with_params():
    # Run the workflow
    try:
        incoming = request.get_json()  # Receive the data as JSON
        creds = incoming.get('creds')
        print("Received:", incoming)   # Log it on the server for visibility

        result = enhance_and_filter_emails_workflow.invoke(AgentState(emails=[], filtered_emails=[], email_creds=creds))
        emails = result.get("emails", [])

        if not emails:
            print("ℹ️ No emails returned by workflow.")
            return jsonify({"message": "No emails returned by workflow.", "emails": []}), 200
        else:
            filtered_emails = [
        {k: v for k, v in email.items() if k != "body"}
        for email in emails
    ]
            for email in emails:
                send_email_payload(email)
            return jsonify({"message": "Emails processed and sent.", "emails": filtered_emails}), 200
        # return jsonify({"message": "Workflow execution is currently disabled."}), 200

    except Exception as main_err:
        print(f"🚨 Failed to run workflow: {main_err}")
        return jsonify({"error": str(main_err)}), 500



if __name__ == "__main__":
    app.run(debug=True)