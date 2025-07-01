from langgraph.graph import StateGraph
from typing import Dict, List

from .fetch_emails import get_emails, mark_email_as_read
from .gmail_auth import authenticate_gmail
from googleapiclient.discovery import build
from agents._tools.llm_emailAgent import return_email_label
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
   
    logs = []
    creds = authenticate_gmail()
    history_text=db_history_text = (
    "Email 1: Initial Outreach - Exploring Collaboration Opportunities\n"
    "From: anca.hiciu0@gmail.com\n"
    "To: gabrielnistor659@gmail.com\n"
    "Subject: Exploring New Collaboration Opportunities\n"
    "Date: May 5, 2025\n"
    "\n"
    "Dear Gabriel,\n"
    "\n"
    "We are excited to reach out and explore potential collaboration opportunities that could benefit both parties. Could you please let us know your availability for a quick call next week to discuss our vision and how we might work together?\n"
    "\n"
    "Best regards,\n"
    "Company A Team\n"
    "\n"
    "Suggested Action: Schedule a call to discuss potential collaboration.\n"
    "\n"
    "---------------------------------------------------------\n"
    "\n"
    "Email 2: Follow-Up on Proposal – Q3 Partnership\n"
    "From: anca.hiciu0@gmail.com\n"
    "To: gabrielnistor659@gmail.com\n"
    "Subject: Follow-Up: Q3 Partnership Proposal\n"
    "Date: May 19, 2025\n"
    "\n"
    "Hello Gabriel,\n"
    "\n"
    "Following our initial conversation, we have put together a detailed proposal for a Q3 partnership. Attached, you will find the document outlining the key points and benefits of the potential partnership. We look forward to hearing your thoughts and any feedback you might have.\n"
    "\n"
    "Warm regards,\n"
    "Company A Partnership Team\n"
    "\n"
    "Suggested Action: Review the Q3 partnership proposal and send your feedback.\n"
    "\n"
    "---------------------------------------------------------\n"
    "\n"
    "Email 3: Clarification on Service Offerings\n"
    "From: anca.hiciu0@gmail.com.com\n"
    "To: gabrielnistor659@gmail.com\n"
    "Subject: Clarification on Our Service Offerings\n"
    "Date: June 8, 2025\n"
    "\n"
    "Dear Gabriel,\n"
    "\n"
    "In response to your recent queries regarding our service offerings, please find the attached document that provides detailed explanations of our various services. We hope this clears up any ambiguities. Do let us know if you need further clarification or have additional questions.\n"
    "\n"
    "Sincerely,\n"
    "Company A Support Team\n"
    "\n"
    "Suggested Action: Review the detailed service offerings and follow up with any questions."
    )
    for email in state["emails"]:

        db_history_text = history_text if email.get("id") == "197a111580ad8eab" else ""
        result=return_email_label(email["body"],db_history_text)
        label=result["category"]
        actionable=result.get("actionable")
        short_description=result["short_description"]
        suggested_action=result.get("suggested_action")
        relevance=result.get("relevance")
        email["label"] = label 
        email["actionable"] = actionable
        email["short_description"] = short_description 
        email["suggested_action"] = suggested_action 
        email["relevance"] = relevance
        apply_gmail_label(creds, email, label,logs)
    state["logs"] = logs
    return state

def apply_gmail_label(creds, email, label_name,log_list):
    """Apply a single Gmail label to an email, creating it if it doesn't exist."""
    service = build('gmail', 'v1', credentials=creds)
    
    # Extract email id and current labels from the email object
    label_list = service.users().labels().list(userId='me').execute()
    email_id = email.get("id")
    id_to_name = {label['id']: label['name'] for label in label_list['labels']}
    current_label_Ids = email.get("labelIds", [])
    current_labels = [id_to_name.get(label_id, f"(Unknown: {label_id})") for label_id in current_label_Ids]

    # Define the allowed set of labels.
    unallowed_labels = {
        "Actionable", "Informative",
        "Invoice", "Contract", 
        "Promo",
    }

    # Only process emails if every label currently attached is in the allowed set.
    if set(current_labels).intersection(unallowed_labels):
        doubleLabel = set(current_labels).intersection(unallowed_labels)
        print(f"Email {email_id} already has label {doubleLabel}. Skipping label application.")
        return

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
        print(f"✅ Actionable '{email.get("actionable")}' for email {email_id}")
        print(f"✅ Suggested_action '{email.get("suggested_action")}' for email {email_id}")
        print(f"✅ Relevance '{email.get("relevance")}' for email {email_id}")

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
if __name__ == "__main__":
    result = workflow.invoke({})

