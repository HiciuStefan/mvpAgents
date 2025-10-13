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
    for email in state.emails:
        try:
            # parse + validate into a Pydantic model
            enhancement = get_email_enhancements(email_text=email["body"])

            # unpack the validated fields back into the email dict

            email["short_description"] = enhancement.analysis.short_description
            email["priority_level"]    = enhancement.analysis.priority_level
            email["opportunity_type"]  = enhancement.analysis.opportunity_type
            email["actionable"]      = enhancement.analysis.actionable
            email["suggested_action"]  = enhancement.analysis.suggested_action
            email["relevance"]       = enhancement.analysis.relevance
            email["suggested_reply"]   = enhancement.analysis.suggested_reply

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

def set_actionable_emails(state: AgentState) -> AgentState:
    state.filtered_emails = [
        email for email in state.emails
        if email.get("actionable") is True
    ]
    return state

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("fetch_emails", fetch_emails)
builder.add_node("enhance_emails_with_llm_response", enhance_emails_with_llm_response)
builder.add_node("set_actionable_emails", set_actionable_emails)
builder.set_entry_point("fetch_emails")
builder.add_edge("fetch_emails", "enhance_emails_with_llm_response")
builder.add_edge("enhance_emails_with_llm_response", "set_actionable_emails")

enhance_and_filter_emails_workflow = builder.compile()

