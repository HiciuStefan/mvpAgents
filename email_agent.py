from langgraph.graph import StateGraph
from typing import Dict, List

from fetch_emails import get_emails, mark_email_as_read
from gmail_auth import authenticate_gmail
from sentiment import analyze_sentiment
from googleapiclient.discovery import build
from get_label import return_email_label
from googleapiclient.errors import HttpError

# Define the state (shared data between nodes)
class AgentState(Dict):
    emails: List[Dict]
    filtered_emails: List[Dict]

# Nodes
def fetch_emails(state: AgentState) -> AgentState:
    creds = authenticate_gmail()  
    state["emails"] = get_emails(creds)
    return state

def filter_emails(state: AgentState) -> AgentState:
    negative_or_urgent = []
    logs = []
    creds = authenticate_gmail()

    for email in state["emails"]:
        sentiment = analyze_sentiment(email["body"])
        if sentiment in ["negative", "urgent"]:
            negative_or_urgent.append(email)
            email["sentiment"] = sentiment

        label=return_email_label(email["body"])
        email["tag"] = label 
        apply_gmail_label(creds, email["id"], label,logs)
    state["filtered_emails"] = negative_or_urgent
    state["logs"] = logs
    return state

def apply_gmail_label(creds, email_id, label_name,log_list):
    """Apply a single Gmail label to an email, creating it if it doesn't exist."""
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Fetch existing labels
        existing_labels = service.users().labels().list(userId='me').execute().get('labels', [])
        label_id = None
        for label in existing_labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break

        # If label doesn't exist, create it
        if not label_id:
            new_label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = service.users().labels().create(userId='me', body=new_label).execute()
            label_id = created_label['id']
            log_list.append(f"🆕 Created label '{label_name}'")
            print(f"🆕 Created label '{label_name}'")

        # Apply label to the email
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={"addLabelIds": [label_id]}
        ).execute()

        print(f"✅ Applied label '{label_name}' to email {email_id}")

    except HttpError as error:
        print(f"❌ An error occurred: {error}")

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("fetch_emails", fetch_emails)
builder.add_node("filter_emails", filter_emails)
builder.set_entry_point("fetch_emails")
builder.add_edge("fetch_emails", "filter_emails")

workflow = builder.compile()

# Run the agent
result = workflow.invoke({})

