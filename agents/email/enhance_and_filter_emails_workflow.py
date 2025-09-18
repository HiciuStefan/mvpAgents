import logging
from langgraph.graph import StateGraph
from typing import Dict, List, Optional

from .fetch_emails import get_emails
from .gmail_auth import authenticate_gmail
from googleapiclient.discovery import build
from .._tools.llm_emailAgent import get_email_enhancements
from googleapiclient.errors import HttpError
from google.auth.credentials import Credentials 
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    emails: List[Dict]
    filtered_emails: List[Dict]
    email_creds: Optional[Credentials] = Field(default=None, exclude=True)
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    # logs: List[str]

# Nodes
def fetch_emails(state: AgentState) -> AgentState:
    
    if(state.email_creds is None):
        gmail_creds = authenticate_gmail()  
        state.email_creds = gmail_creds
        state.emails = get_emails(gmail_creds)
    else:
        state.emails = get_emails(state.email_creds)
        
    return state

def enhance_emails_with_llm_response(state: AgentState) -> AgentState:
   
    # logs = []
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
    for email in state.emails:

        db_history_text = history_text if email.get("id") == "197a111580ad8eab" else ""
        
        try:
            # parse + validate into a Pydantic model
            enhancement = get_email_enhancements(
                email_text=email["body"],
                db_history_text=db_history_text)

            # unpack the validated fields back into the email dict

            email["short_description"] = enhancement.short_description
            email["actionable"]      = enhancement.actionable
            email["suggested_action"]  = enhancement.suggested_action
            email["relevance"]       = enhancement.relevance
            email["suggested_reply"]   = enhancement.suggested_reply

        except RuntimeError as e:
            # TODO remove print, use logging
            # either JSON parse or validation failed
            # print(f"⚠️ Skipping email {email['id']}: {e}")

            logger = logging.getLogger(__name__)
            logger.error("❌ JSON parsing failed", exc_info=e)

            continue

    # TODO remove as this is not used anymore    
    # state["logs"] = logs

    return state

def filter_emails(state: AgentState) -> AgentState:
    state.filtered_emails = [
        email for email in state.emails
        if email.get("actionable") is True
    ]
    return state

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("fetch_emails", fetch_emails)
builder.add_node("enhance_emails_with_llm_response", enhance_emails_with_llm_response)
builder.add_node("filter_emails", filter_emails)
builder.set_entry_point("fetch_emails")
builder.add_edge("fetch_emails", "enhance_emails_with_llm_response")
builder.add_edge("enhance_emails_with_llm_response", "filter_emails")

enhance_and_filter_emails_workflow = builder.compile()

