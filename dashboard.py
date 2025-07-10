import streamlit as st

import json
import pandas as pd
import requests
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import io
import base64

CAMPAIGNS_FILE = "campaigns_data.json"
TEMP_CAMPAIGN_FILE = "temp_campaign_data.json"

from campaign import Campaign
from sostac_questions import SOSTAC_QUESTIONS
from llm_marketing_agent import MarketingAgent  



# Configure page
st.set_page_config(
    page_title="Marketing Campaign Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = {}
if 'current_campaign' not in st.session_state:
    st.session_state.current_campaign = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0



def render_question(question_data: Dict, section: str) -> any:
    """Render individual question based on type"""
    key = f"{section}_{question_data['key']}"
    
    if question_data["type"] == "radio":
        return st.radio(question_data["question"], question_data["options"], key=key)
    elif question_data["type"] == "selectbox":
        return st.selectbox(question_data["question"], question_data["options"], key=key)
    elif question_data["type"] == "multiselect":
        return st.multiselect(question_data["question"], question_data["options"], key=key)
    elif question_data["type"] == "text_input":
        return st.text_input(question_data["question"], key=key)
    elif question_data["type"] == "text_area":
        return st.text_area(question_data["question"], key=key)

# def collect_sostac_data() -> Dict:
    # """Collect all SOSTAC responses from session state"""
    # sostac_data = {}
    # for section, section_data in SOSTAC_QUESTIONS.items():
    #     sostac_data[section] = {}
    #     for question in section_data["questions"]:
    #         key = f"{section}_{question['key']}"
    #         sostac_data[section][question['key']] = st.session_state.get(key, "")
    # return sostac_data

def dashboard_page():
    """Main dashboard for managing campaigns"""
    st.title("🚀 Marketing Campaign Agent")
    st.markdown("### Your AI-Powered Marketing Campaign Creator")
    
    # Campaign stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Campaigns", len(st.session_state.campaigns))
    
    with col2:
        approved_campaigns = sum(1 for c in st.session_state.campaigns.values() if c.approved)
        st.metric("Approved Campaigns", approved_campaigns)
    
    with col3:
        st.metric("Active Campaigns", approved_campaigns)  # Simplified for MVP
    
    with col4:
        st.metric("Success Rate", "85%")  # Placeholder
    
    st.markdown("---")
    
    # Create new campaign button
    if st.button("🎯 Create New Campaign", type="primary", use_container_width=True):
        st.session_state.page = "create_campaign"
        st.session_state.current_step = 0
        clear_temp_campaign_data()
        st.rerun()
    
    # Display existing campaigns
    if st.session_state.campaigns:
        st.markdown("### Your Campaigns")
        
        for campaign_id, campaign in st.session_state.campaigns.items():
            with st.expander(f"📊 {campaign.name}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Created:** {campaign.created_at[:10]}")
                    st.write(f"**Status:** {'✅ Approved' if campaign.approved else '⏳ Pending'}")
                    st.write(f"**Industry:** {campaign.sostac_data.get('situation', {}).get('industry', 'N/A')}")
                
                with col2:
                    if st.button(f"Edit", key=f"edit_{campaign_id}"):
                        st.session_state.current_campaign = campaign_id
                        st.session_state.page = "edit_campaign"
                        st.rerun()
                
                with col3:
                    if st.button(f"View", key=f"view_{campaign_id}"):
                        st.session_state.current_campaign = campaign_id
                        st.session_state.page = "view_campaign"
                        st.rerun()

def load_campaigns_from_file() -> Dict:
    """Load campaigns from local JSON file"""
    try:
        if os.path.exists(CAMPAIGNS_FILE):
            with open(CAMPAIGNS_FILE, 'r') as f:
                data = json.load(f)
                return data
        return {}
    except Exception as e:
        st.error(f"Error loading campaigns: {e}")
        return {}

def save_campaigns_to_file(campaigns: Dict) -> bool:
    """Save campaigns to local JSON file"""
    try:
        # Convert Campaign objects to dictionaries for JSON serialization
        serializable_campaigns = {}
        for campaign_id, campaign in campaigns.items():
            serializable_campaigns[campaign_id] = {
                "name": campaign.name,
                "sostac_data": campaign.sostac_data,
                "strategy": campaign.strategy,
                "deliverables": campaign.deliverables,
                "influencers": campaign.influencers,
                "approved": campaign.approved,
                "created_at": campaign.created_at
            }
        
        with open(CAMPAIGNS_FILE, 'w') as f:
            json.dump(serializable_campaigns, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving campaigns: {e}")
        return False

def save_temp_campaign_data(data: Dict) -> bool:
    """Save temporary campaign data during creation process"""
    try:
        temp_data = {
            "timestamp": datetime.now().isoformat(),
            "current_step": st.session_state.get("current_step", 0),
            "campaign_data": data
        }
        with open(TEMP_CAMPAIGN_FILE, 'w') as f:
            json.dump(temp_data, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving temporary data: {e}")
        return False

def load_temp_campaign_data() -> Optional[Dict]:
    """Load temporary campaign data"""
    try:
        if os.path.exists(TEMP_CAMPAIGN_FILE):
            with open(TEMP_CAMPAIGN_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error loading temporary data: {e}")
        return None

def clear_temp_campaign_data():
    """Clear temporary campaign data"""
    try:
        if os.path.exists(TEMP_CAMPAIGN_FILE):
            os.remove(TEMP_CAMPAIGN_FILE)
    except Exception as e:
        st.error(f"Error clearing temporary data: {e}")

def collect_sostac_data_improved() -> Dict:
    """Improved SOSTAC data collection with file backup"""
    sostac_data = {}
    
    # First, try to get from session state
    for section, section_data in SOSTAC_QUESTIONS.items():
        sostac_data[section] = {}
        for question in section_data["questions"]:
            key = f"{section}_{question['key']}"
            value = st.session_state.get(key, "")
            sostac_data[section][question['key']] = value
    
    # If session state is empty, try to load from temp file
    if not any(any(section_data.values()) for section_data in sostac_data.values()):
        temp_data = load_temp_campaign_data()
        if temp_data and "campaign_data" in temp_data:
            sostac_data = temp_data["campaign_data"].get("sostac_data", sostac_data)
    
    return sostac_data

def get_campaign_name_improved() -> str:
    """Get campaign name with fallback to temp file"""
    # First try session state
    campaign_name = st.session_state.get("campaign_name", "")
    
    # If empty, try temp file
    if not campaign_name:
        temp_data = load_temp_campaign_data()
        if temp_data and "campaign_data" in temp_data:
            campaign_name = temp_data["campaign_data"].get("campaign_name", "")
    
    return campaign_name

def auto_save_progress():
    """Auto-save progress during campaign creation"""
    if st.session_state.get("current_step", 0) > 0:
        # Collect all current data
        current_data = {
            "campaign_name": st.session_state.get("campaign_name", ""),
            "campaign_description": st.session_state.get("campaign_description", ""),
            "sostac_data": collect_sostac_data_improved(),
            "current_step": st.session_state.get("current_step", 0)
        }
        
        # Save to temp file
        save_temp_campaign_data(current_data)

def initialize_session_state():
    """Initialize session state with data from files if available"""
    
    # Load campaigns from file if session state is empty
    if 'campaigns' not in st.session_state or not st.session_state.campaigns:
        file_campaigns = load_campaigns_from_file()
        if file_campaigns:
            # Convert back to Campaign objects
            campaigns = {}
            for campaign_id, campaign_data in file_campaigns.items():
                campaign = Campaign(
                    name=campaign_data["name"],
                    sostac_data=campaign_data["sostac_data"]
                )
                campaign.strategy = campaign_data.get("strategy")
                campaign.deliverables = campaign_data.get("deliverables")
                campaign.influencers = campaign_data.get("influencers")
                campaign.approved = campaign_data.get("approved", False)
                campaign.created_at = campaign_data.get("created_at", datetime.now().isoformat())
                campaigns[campaign_id] = campaign
            
            st.session_state.campaigns = campaigns
    
    # Load temporary campaign data if in creation process
    if (
        st.session_state.get("page") == "create_campaign"
        and (("current_step" not in st.session_state) or st.session_state.current_step == 0)
    ):
        temp_data = load_temp_campaign_data()
        if temp_data and "campaign_data" in temp_data:
            campaign_data = temp_data["campaign_data"]

            if "campaign_name" in campaign_data:
                st.session_state["campaign_name"] = campaign_data["campaign_name"]

            if "campaign_description" in campaign_data:
                st.session_state["campaign_description"] = campaign_data["campaign_description"]

            if "current_step" in campaign_data:
                st.session_state["current_step"] = campaign_data["current_step"]

            # Restore SOSTAC data
            if "sostac_data" in campaign_data:
                for section, section_data in campaign_data["sostac_data"].items():
                    for key, value in section_data.items():
                        session_key = f"{section}_{key}"
                        if value:
                            st.session_state[session_key] = value
    # if st.session_state.get("page") == "create_campaign":
    #     temp_data = load_temp_campaign_data()
    #     if temp_data and "campaign_data" in temp_data:
    #         campaign_data = temp_data["campaign_data"]
            
    #         # Restore session state from temp file
    #         if "campaign_name" in campaign_data:
    #             st.session_state["campaign_name"] = campaign_data["campaign_name"]
            
    #         if "campaign_description" in campaign_data:
    #             st.session_state["campaign_description"] = campaign_data["campaign_description"]
            
    #         if "current_step" in campaign_data:
    #             st.session_state["current_step"] = campaign_data["current_step"]
            
    #         # Restore SOSTAC data
    #         if "sostac_data" in campaign_data:
    #             for section, section_data in campaign_data["sostac_data"].items():
    #                 for key, value in section_data.items():
    #                     session_key = f"{section}_{key}"
    #                     if value:  # Only restore non-empty values
    #                         st.session_state[session_key] = value

# auto_save_progress (saves in temp_campaign_data.json) is called automatically on next and previous buttons click
# save_campaigns_to_file saves to campaigns_data.json on create campaign
# temp_campaign_data.json is loaded automatically when creating a new campaign if it contains data
def create_campaign_page_improved():
    """Improved campaign creation with better data persistence"""
    st.title("🎯 Create New Campaign")
    
    # Auto-save progress
    auto_save_progress()
    
    # Progress indicator
    steps = ["Basic Info", "Situation", "Objectives", "Strategy", "Tactics", "Actions", "Control", "Review"]
    current_step = st.session_state.current_step
    
    # Progress bar
    progress = (current_step + 1) / len(steps)
    st.progress(progress)
    
    # Step indicator
    st.markdown(f"**Step {current_step + 1} of {len(steps)}: {steps[current_step]}**")
    
    # Add data recovery option
    if st.button("🔄 Load Previously Saved Data"):
        temp_data = load_temp_campaign_data()
        if temp_data:
            st.success("Previous data loaded successfully!")
            st.rerun()
        else:
            st.info("No previous data found.")
    
    if current_step == 0:
        # Basic campaign info
        st.markdown("### Campaign Information")
        
        # Get campaign name with improved fallback
        current_name = get_campaign_name_improved()
        campaign_name = st.text_input("Campaign Name", value=current_name, key="campaign_name")
        
        current_desc = st.session_state.get("campaign_description", "")
        campaign_description = st.text_area("Campaign Description (Optional)", 
                                          value=current_desc, key="campaign_description")
        
        # Show what we currently have
        if campaign_name or campaign_description:
            st.info(f"Current data: Name='{campaign_name}', Description='{campaign_description[:50]}...'")
        
        if st.button("Next", disabled=not campaign_name):
            # Save progress before moving to next step
            auto_save_progress()
            st.session_state.current_step = 1
            st.rerun()
    
    elif current_step in [1, 2, 3, 4, 5, 6]:
        # SOSTAC questions
        section_keys = list(SOSTAC_QUESTIONS.keys())
        section_key = section_keys[current_step - 1]
        section_data = SOSTAC_QUESTIONS[section_key]
        
        st.markdown(f"### {section_data['title']}")
        
        # Show current progress
        current_responses = 0
        total_questions = len(section_data["questions"])
        
        for question in section_data["questions"]:
            render_question(question, section_key)
            key = f"{section_key}_{question['key']}"
            if st.session_state.get(key):
                current_responses += 1
        
        st.progress(current_responses / total_questions)
        st.write(f"Progress: {current_responses}/{total_questions} questions answered")
        
        # Navigation
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Previous") and current_step > 0:
                auto_save_progress()
                st.session_state.current_step -= 1
                st.rerun()
        
        with col2:
            if st.button("💾 Save Progress"):
                auto_save_progress()
                st.success("Progress saved!")
        
        with col3:
            if st.button("Next"):
                auto_save_progress()
                st.session_state.current_step += 1
                st.rerun()
    
    elif current_step == 7:
        # Review and create campaign
        st.markdown("### Review Your Campaign")
        
        # Get data with improved methods
        sostac_data = collect_sostac_data_improved()
        campaign_name = get_campaign_name_improved()
        
        # Show data collection status
        st.markdown("#### Data Collection Status")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Campaign Name", "✅ Set" if campaign_name else "❌ Missing")
            
        with col2:
            filled_sections = sum(1 for section_data in sostac_data.values() 
                                if any(section_data.values()))
            st.metric("SOSTAC Sections", f"{filled_sections}/6")
        
        # Display summary
        st.markdown("#### Campaign Summary")
        st.write(f"**Name:** {campaign_name if campaign_name else '❌ Not provided'}")
        
        # Show SOSTAC data
        for section, section_data in sostac_data.items():
            if any(section_data.values()):
                with st.expander(f"{section.title()} - ✅ Completed"):
                    for key, value in section_data.items():
                        if value:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.warning(f"{section.title()} - ❌ No data collected")
        
        # Debug section
        with st.expander("🔍 Debug Information"):
            st.write("Campaign Name:", campaign_name)
            st.write("SOSTAC Data:", sostac_data)
            st.write("Session State Keys:", [k for k in st.session_state.keys() if 'campaign' in k or any(s in k for s in ['situation', 'objectives', 'strategy', 'tactics', 'actions', 'control'])])
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous"):
                st.session_state.current_step -= 1
                st.rerun()
        
        with col2:
            can_create = bool(campaign_name and any(any(section_data.values()) for section_data in sostac_data.values()))
            if st.button("Create Campaign", type="primary", disabled=not can_create):
                if can_create:
                    # Create campaign
                    campaign_id = f"campaign_{len(st.session_state.campaigns) + 1}"
                    campaign = Campaign(
                        name=campaign_name,
                        sostac_data=sostac_data
                    )
                    st.session_state.campaigns[campaign_id] = campaign
                    st.session_state.current_campaign = campaign_id
                    
                    # Save to file
                    save_campaigns_to_file(st.session_state.campaigns)
                    
                    # Clear temp data
                    clear_temp_campaign_data()
                    
                    st.session_state.page = "generate_strategy"
                    st.rerun()
                else:
                    st.error("Please complete the campaign name and at least one SOSTAC section.")

# Add this to your main() function
# def main():
#     """Main application entry point with improved data handling"""
    
#     # Initialize session state and load data
#     initialize_session_state()
    
#     # Initialize other session state variables
#     if 'campaigns' not in st.session_state:
#         st.session_state.campaigns = {}
#     if 'current_campaign' not in st.session_state:
#         st.session_state.current_campaign = None
#     if 'current_step' not in st.session_state:
#         st.session_state.current_step = 0
#     if 'page' not in st.session_state:
#         st.session_state.page = "dashboard"
    
#     # Auto-save campaigns periodically
#     if st.session_state.campaigns:
#         save_campaigns_to_file(st.session_state.campaigns)
    
#     # Rest of your existing main() function...
#     # (sidebar navigation, page routing, etc.)

#uses render_question & collect_sostac_data
# def create_campaign_page():
    # """Multi-step campaign creation process"""
    # st.title("🎯 Create New Campaign")
    
    # # Progress indicator
    # steps = ["Basic Info", "Situation", "Objectives", "Strategy", "Tactics", "Actions", "Control", "Review"]
    # current_step = st.session_state.current_step
    
    # # Progress bar
    # progress = (current_step + 1) / len(steps)
    # st.progress(progress)
    
    # # Step indicator
    # st.markdown(f"**Step {current_step + 1} of {len(steps)}: {steps[current_step]}**")
    
    # if current_step == 0:
    #     # Basic campaign info
    #     st.markdown("### Campaign Information")
        
    #     campaign_name = st.text_input("Campaign Name", key="campaign_name")
    #     campaign_description = st.text_area("Campaign Description (Optional)", key="campaign_description")
        
    #     if st.button("Next", disabled=not campaign_name):
    #         st.session_state.current_step = 1
    #         st.rerun()
    
    # elif current_step in [1, 2, 3, 4, 5, 6]:
    #     # SOSTAC questions
    #     section_keys = list(SOSTAC_QUESTIONS.keys())
    #     section_key = section_keys[current_step - 1]
    #     section_data = SOSTAC_QUESTIONS[section_key]
        
    #     st.markdown(f"### {section_data['title']}")
        
    #     # Render questions for this section
    #     for question in section_data["questions"]:
    #         render_question(question, section_key)
        
    #     # Navigation
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         if st.button("Previous") and current_step > 0:
    #             st.session_state.current_step -= 1
    #             st.rerun()
        
    #     with col2:
    #         if st.button("Next"):
    #             st.session_state.current_step += 1
    #             st.rerun()
    
    # elif current_step == 7:
    #     # Review and create campaign
    #     st.markdown("### Review Your Campaign")
        
    #     # Collect all data
    #     sostac_data = collect_sostac_data()
    #     campaign_name = st.session_state.get("campaign_name", "")
        
    #     # Display summary
    #     st.markdown("#### Campaign Summary")
    #     st.write(f"**Name:** {campaign_name}")
    #     st.write(f"**Industry:** {sostac_data.get('situation', {}).get('industry', 'N/A')}")
    #     st.write(f"**Primary Goal:** {sostac_data.get('objectives', {}).get('primary_goal', 'N/A')}")
    #     st.write(f"**Budget:** {sostac_data.get('objectives', {}).get('budget_range', 'N/A')}")
    #     st.write(f"**Duration:** {sostac_data.get('objectives', {}).get('campaign_duration', 'N/A')}")
        
    #     # Navigation
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         if st.button("Previous"):
    #             st.session_state.current_step -= 1
    #             st.rerun()
        
    #     with col2:
    #         if st.button("Create Campaign", type="primary"):
    #             # Create campaign
    #             campaign_id = f"campaign_{len(st.session_state.campaigns) + 1}"
    #             campaign = Campaign(
    #                 name=campaign_name,
    #                 sostac_data=sostac_data
    #             )
    #             st.session_state.campaigns[campaign_id] = campaign
    #             st.session_state.current_campaign = campaign_id
    #             st.session_state.page = "generate_strategy"
    #             st.rerun()

def generate_strategy_page():
    """Generate campaign strategy using AI"""
    st.title("🤖 Generating Campaign Strategy")
    
    if st.session_state.current_campaign:
        campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
        st.markdown(f"### Strategy for: {campaign.name}")
        
        # Initialize marketing agent
        agent = MarketingAgent()
        
        # Get trending topics
        with st.spinner("Analyzing current trends..."):
            trends = agent.get_trending_topics()
            st.success(f"Found {len(trends)} trending topics")
        
        # Analyze competitors
        with st.spinner("Analyzing competitors..."):
            competitors = campaign.sostac_data.get('situation', {}).get('competitors', '').split(',')
            industry = campaign.sostac_data.get('situation', {}).get('industry', '')
            competitor_analysis = agent.analyze_competitors(industry, competitors)
            st.success("Competitor analysis complete")
        
        # Generate strategy
        with st.spinner("Generating comprehensive strategy..."):
            strategy = agent.generate_campaign_strategy(
                campaign.sostac_data, 
                trends, 
                competitor_analysis
            )
        
        # Display strategy
        st.markdown("### Generated Strategy")
        st.markdown(strategy)
        
        # Approval buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❌ Reject & Regenerate"):
                st.rerun()
        
        with col2:
            if st.button("✏️ Edit Strategy"):
                st.session_state.page = "edit_strategy"
                campaign.strategy = strategy
                st.rerun()
        
        with col3:
            if st.button("✅ Approve Strategy", type="primary"):
                campaign.strategy = strategy
                campaign.approved = True
                st.session_state.page = "generate_deliverables"
                st.rerun()

def generate_deliverables_page():
    """Generate campaign deliverables"""
    st.title("📋 Generating Campaign Deliverables")
    
    if st.session_state.current_campaign:
        campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
        st.markdown(f"### Deliverables for: {campaign.name}")
        
        # Initialize agent
        agent = MarketingAgent()
        
        # Generate deliverables
        with st.spinner("Creating detailed deliverables..."):
            deliverables = agent.generate_deliverables(campaign.strategy, campaign.sostac_data)
        
        # Store deliverables
        campaign.deliverables = deliverables
        
        # Display deliverables
        if "error" not in deliverables:
            for deliverable_type, content in deliverables.items():
                with st.expander(f"📄 {deliverable_type.replace('_', ' ').title()}", expanded=True):
                    st.write(content)
        else:
            st.error(deliverables["error"])
        
        # Generate influencer recommendations
        st.markdown("### Influencer Recommendations")
        
        with st.spinner("Finding relevant influencers..."):
            industry = campaign.sostac_data.get('situation', {}).get('industry', '')
            budget = campaign.sostac_data.get('objectives', {}).get('budget_range', '')
            influencers = agent.find_influencers(industry, "US", budget)
        
        campaign.influencers = influencers
        
        # Display influencers
        for influencer in influencers:
            with st.expander(f"👤 {influencer['name']} - {influencer['platform']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Followers:** {influencer['followers']}")
                    st.write(f"**Engagement:** {influencer['engagement_rate']}")
                    st.write(f"**Estimated Cost:** {influencer['estimated_cost']}")
                with col2:
                    st.write(f"**Platform:** {influencer['platform']}")
                    st.write(f"**Niche:** {influencer['niche']}")
                    st.write(f"**Performance:** {influencer['recent_performance']}")
        
        # Final approval
        if st.button("🚀 Launch Campaign", type="primary", use_container_width=True):
            st.success("🎉 Campaign launched successfully!")
            st.balloons()
            st.session_state.page = "dashboard"
            st.rerun()

# def export_campaign_data():
    # """Export campaign data to various formats"""
    # if st.session_state.current_campaign:
    #     campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
    #     # Create export data
    #     export_data = {
    #         "Campaign Name": campaign.name,
    #         "Created": campaign.created_at,
    #         "Status": "Approved" if campaign.approved else "Draft",
    #         "Industry": campaign.sostac_data.get('situation', {}).get('industry', 'N/A'),
    #         "Budget": campaign.sostac_data.get('objectives', {}).get('budget_range', 'N/A'),
    #         "Duration": campaign.sostac_data.get('objectives', {}).get('campaign_duration', 'N/A'),
    #         "Primary Goal": campaign.sostac_data.get('objectives', {}).get('primary_goal', 'N/A'),
    #         "Strategy": campaign.strategy or "Not generated",
    #         "Deliverables": str(campaign.deliverables) if campaign.deliverables else "Not generated"
    #     }
        
    #     # Convert to DataFrame for CSV export
    #     df = pd.DataFrame([export_data])
        
    #     # Export options
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         csv_data = df.to_csv(index=False)
    #         st.download_button(
    #             label="📄 Download CSV",
    #             data=csv_data,
    #             file_name=f"{campaign.name}_export.csv",
    #             mime="text/csv"
    #         )
        
    #     with col2:
    #         json_data = json.dumps(export_data, indent=2)
    #         st.download_button(
    #             label="📋 Download JSON",
    #             data=json_data,
    #             file_name=f"{campaign.name}_export.json",
    #             mime="application/json"
    #         )
        
    #     with col3:
    #         # For PDF, we'd need additional libraries
    #         st.info("PDF export coming soon!")

def export_campaign_data(campaign_id: str = None):
    """
    Export campaign data to various formats with proper UI integration
    """
    # Use current campaign if no specific campaign_id provided
    if campaign_id is None:
        campaign_id = st.session_state.current_campaign
    
    if not campaign_id or campaign_id not in st.session_state.campaigns:
        st.error("No campaign selected for export")
        return
    
    campaign = st.session_state.campaigns[campaign_id]
    
    st.markdown("### 📤 Export Campaign Data")
    st.markdown(f"**Campaign:** {campaign.name}")
    
    # Export format selection
    export_format = st.selectbox(
        "Select Export Format:",
        ["CSV", "JSON", "Excel", "PDF Summary", "Full Report"]
    )
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        include_strategy = st.checkbox("Include Strategy", value=True)
        include_deliverables = st.checkbox("Include Deliverables", value=True)
        include_influencers = st.checkbox("Include Influencers", value=True)
    
    with col2:
        include_sostac = st.checkbox("Include SOSTAC Analysis", value=True)
        include_performance = st.checkbox("Include Performance Data", value=False)
        include_timestamps = st.checkbox("Include Timestamps", value=True)
    
    # Generate export data
    if st.button("🔄 Generate Export", type="primary"):
        with st.spinner("Generating export data..."):
            
            # Create comprehensive export data
            export_data = create_export_data(
                campaign, 
                include_strategy, 
                include_deliverables, 
                include_influencers,
                include_sostac,
                include_performance,
                include_timestamps
            )
            
            # Generate file based on format
            if export_format == "CSV":
                file_data, filename = generate_csv_export(export_data, campaign.name)
                download_button(file_data, filename, "text/csv")
                
            elif export_format == "JSON":
                file_data, filename = generate_json_export(export_data, campaign.name)
                download_button(file_data, filename, "application/json")
                
            elif export_format == "Excel":
                file_data, filename = generate_excel_export(export_data, campaign)
                download_button(file_data, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
            elif export_format == "PDF Summary":
                file_data, filename = generate_pdf_summary(export_data, campaign.name)
                download_button(file_data, filename, "application/pdf")
                
            elif export_format == "Full Report":
                file_data, filename = generate_full_report(export_data, campaign)
                download_button(file_data, filename, "text/markdown")
            
            st.success(f"✅ Export generated successfully as {export_format}")

def create_export_data(campaign, include_strategy=True, include_deliverables=True, 
                      include_influencers=True, include_sostac=True, 
                      include_performance=False, include_timestamps=True) -> Dict[str, Any]:
    """
    Create comprehensive export data structure
    """
    export_data = {
        "campaign_info": {
            "name": campaign.name,
            "status": "Approved" if campaign.approved else "Draft",
            "industry": campaign.sostac_data.get('situation', {}).get('industry', 'N/A'),
            "budget": campaign.sostac_data.get('objectives', {}).get('budget_range', 'N/A'),
            "duration": campaign.sostac_data.get('objectives', {}).get('campaign_duration', 'N/A'),
            "primary_goal": campaign.sostac_data.get('objectives', {}).get('primary_goal', 'N/A'),
        }
    }
    
    if include_timestamps:
        export_data["timestamps"] = {
            "created_at": campaign.created_at,
            "exported_at": datetime.now().isoformat()
        }
    
    if include_sostac:
        export_data["sostac_analysis"] = campaign.sostac_data
    
    if include_strategy and campaign.strategy:
        export_data["strategy"] = campaign.strategy
    
    if include_deliverables and campaign.deliverables:
        export_data["deliverables"] = campaign.deliverables
    
    if include_influencers and campaign.influencers:
        export_data["influencers"] = campaign.influencers
    
    if include_performance:
        # Generate mock performance data for now
        export_data["performance"] = generate_performance_data(campaign.name)
    
    return export_data

def generate_csv_export(export_data: Dict, campaign_name: str) -> tuple:
    """
    Generate CSV export with flattened data structure
    """
    # Flatten the data for CSV format
    flattened_data = []
    
    # Campaign info
    for key, value in export_data.get("campaign_info", {}).items():
        flattened_data.append({"Category": "Campaign Info", "Field": key, "Value": str(value)})
    
    # SOSTAC data
    if "sostac_analysis" in export_data:
        for section, section_data in export_data["sostac_analysis"].items():
            for field, value in section_data.items():
                flattened_data.append({
                    "Category": f"SOSTAC - {section.title()}", 
                    "Field": field, 
                    "Value": str(value)
                })
    
    # Influencers
    if "influencers" in export_data:
        for i, influencer in enumerate(export_data["influencers"]):
            for field, value in influencer.items():
                flattened_data.append({
                    "Category": f"Influencer {i+1}", 
                    "Field": field, 
                    "Value": str(value)
                })
    
    # Performance data
    if "performance" in export_data:
        for key, value in export_data["performance"].items():
            flattened_data.append({"Category": "Performance", "Field": key, "Value": str(value)})
    
    # Create DataFrame and convert to CSV
    df = pd.DataFrame(flattened_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    filename = f"{campaign_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return csv_data, filename

def generate_json_export(export_data: Dict, campaign_name: str) -> tuple:
    """
    Generate JSON export with full data structure
    """
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    filename = f"{campaign_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return json_data, filename

def generate_excel_export(export_data: Dict, campaign) -> tuple:
    """
    Generate Excel export with multiple sheets
    """
    # Create Excel buffer
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Campaign Overview Sheet
        campaign_info = pd.DataFrame([export_data.get("campaign_info", {})])
        campaign_info.to_excel(writer, sheet_name='Campaign Overview', index=False)
        
        # SOSTAC Analysis Sheet
        if "sostac_analysis" in export_data:
            sostac_rows = []
            for section, section_data in export_data["sostac_analysis"].items():
                for field, value in section_data.items():
                    sostac_rows.append({
                        "Section": section.title(),
                        "Field": field,
                        "Value": str(value)
                    })
            
            sostac_df = pd.DataFrame(sostac_rows)
            sostac_df.to_excel(writer, sheet_name='SOSTAC Analysis', index=False)
        
        # Influencers Sheet
        if "influencers" in export_data:
            influencers_df = pd.DataFrame(export_data["influencers"])
            influencers_df.to_excel(writer, sheet_name='Influencers', index=False)
        
        # Performance Sheet
        if "performance" in export_data:
            performance_df = pd.DataFrame([export_data["performance"]])
            performance_df.to_excel(writer, sheet_name='Performance', index=False)
        
        # Strategy Sheet (as text)
        if "strategy" in export_data:
            strategy_df = pd.DataFrame([{"Strategy": export_data["strategy"]}])
            strategy_df.to_excel(writer, sheet_name='Strategy', index=False)
    
    excel_buffer.seek(0)
    filename = f"{campaign.name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return excel_buffer.getvalue(), filename

def generate_pdf_summary(export_data: Dict, campaign_name: str) -> tuple:
    """
    Generate PDF summary (simplified markdown for now)
    """
    # Create markdown content for PDF
    markdown_content = f"""
# Campaign Export Summary

## Campaign: {campaign_name}

### Campaign Overview
"""
    
    # Add campaign info
    if "campaign_info" in export_data:
        for key, value in export_data["campaign_info"].items():
            markdown_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    # Add export timestamp
    if "timestamps" in export_data:
        markdown_content += f"\n**Exported**: {export_data['timestamps']['exported_at']}\n"
    
    # Add strategy summary
    if "strategy" in export_data:
        markdown_content += f"\n### Strategy Summary\n{export_data['strategy'][:500]}...\n"
    
    # Add influencer count
    if "influencers" in export_data:
        markdown_content += f"\n### Influencers\n{len(export_data['influencers'])} influencers identified\n"
    
    filename = f"{campaign_name}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    return markdown_content, filename

def generate_full_report(export_data: Dict, campaign) -> tuple:
    """
    Generate comprehensive markdown report
    """
    markdown_content = f"""
# Complete Campaign Report

## Campaign: {campaign.name}

### Executive Summary
"""
    
    # Campaign info
    if "campaign_info" in export_data:
        markdown_content += "#### Campaign Details\n"
        for key, value in export_data["campaign_info"].items():
            markdown_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    # Strategy
    if "strategy" in export_data:
        markdown_content += f"\n## Campaign Strategy\n{export_data['strategy']}\n"
    
    # Deliverables
    if "deliverables" in export_data:
        markdown_content += "\n## Campaign Deliverables\n"
        for deliverable_type, content in export_data["deliverables"].items():
            markdown_content += f"\n### {deliverable_type.replace('_', ' ').title()}\n"
            markdown_content += f"{content}\n"
    
    # Influencers
    if "influencers" in export_data:
        markdown_content += "\n## Influencer Recommendations\n"
        for i, influencer in enumerate(export_data["influencers"], 1):
            markdown_content += f"\n### Influencer {i}: {influencer.get('name', 'N/A')}\n"
            for key, value in influencer.items():
                if key != 'name':
                    markdown_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    # Performance
    if "performance" in export_data:
        markdown_content += "\n## Performance Metrics\n"
        for key, value in export_data["performance"].items():
            markdown_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    # Footer
    markdown_content += f"\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    filename = f"{campaign.name}_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    return markdown_content, filename

def generate_performance_data(campaign_name: str) -> Dict:
    """
    Generate realistic performance data for export
    """
    # This would be replaced with actual performance tracking
    return {
        "impressions": 125000,
        "clicks": 8500,
        "conversions": 342,
        "ctr_percentage": 6.8,
        "conversion_rate_percentage": 4.0,
        "cost_per_click": 1.25,
        "cost_per_conversion": 31.50,
        "roi_multiplier": 3.2,
        "engagement_rate_percentage": 5.4,
        "reach": 89000,
        "total_spend": 10773.00,
        "revenue_generated": 34473.60
    }

def download_button(file_data, filename: str, mime_type: str):
    """
    Create download button for the generated file
    """
    if isinstance(file_data, str):
        file_data = file_data.encode('utf-8')
    
    st.download_button(
        label=f"📥 Download {filename}",
        data=file_data,
        file_name=filename,
        mime=mime_type,
        use_container_width=True
    )

#uses export_campaign_data
def view_campaign_page():
    """View campaign details and performance"""
    if st.session_state.current_campaign:
        campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
        st.title(f"📊 {campaign.name}")
        
        # Campaign overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "✅ Active" if campaign.approved else "⏳ Draft")
        with col2:
            st.metric("Budget", campaign.sostac_data.get('objectives', {}).get('budget_range', 'N/A'))
        with col3:
            st.metric("Duration", campaign.sostac_data.get('objectives', {}).get('campaign_duration', 'N/A'))
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Strategy", "Deliverables", "Influencers", "Performance"])
        
        with tab1:
            if campaign.strategy:
                st.markdown(campaign.strategy)
            else:
                st.info("Strategy not generated yet")
        
        with tab2:
            if campaign.deliverables:
                for deliverable_type, content in campaign.deliverables.items():
                    with st.expander(f"📄 {deliverable_type.replace('_', ' ').title()}"):
                        st.write(content)
            else:
                st.info("Deliverables not generated yet")
        
        with tab3:
            if campaign.influencers:
                for influencer in campaign.influencers:
                    with st.expander(f"👤 {influencer['name']} - {influencer['platform']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Followers:** {influencer['followers']}")
                            st.write(f"**Engagement:** {influencer['engagement_rate']}")
                        with col2:
                            st.write(f"**Cost:** {influencer['estimated_cost']}")
                            st.write(f"**Performance:** {influencer['recent_performance']}")
            else:
                st.info("Influencer recommendations not generated yet")
        
        with tab4:
            # Mock performance data
            st.markdown("### Campaign Performance")
            
            # Sample metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Impressions", "125K", "12%")
            with col2:
                st.metric("Clicks", "8.5K", "15%")
            with col3:
                st.metric("Conversions", "342", "8%")
            with col4:
                st.metric("ROI", "3.2x", "0.5x")
            
            # Sample chart
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            data = pd.DataFrame({
                'Date': dates,
                'Impressions': [1000 + i*100 + (i%7)*200 for i in range(30)],
                'Clicks': [50 + i*5 + (i%7)*10 for i in range(30)],
                'Conversions': [2 + i*0.5 + (i%7)*1 for i in range(30)]
            })
            
            fig = px.line(data, x='Date', y=['Impressions', 'Clicks', 'Conversions'], 
                         title='Campaign Performance Over Time')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        with st.expander("📤 Export Campaign Data", expanded=False):
            export_campaign_data()

        # Back to dashboard
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

def edit_strategy_page():
    """Edit campaign strategy"""
    if st.session_state.current_campaign:
        campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
        st.title(f"✏️ Edit Strategy: {campaign.name}")
        
        # Editable strategy
        edited_strategy = st.text_area(
            "Campaign Strategy",
            value=campaign.strategy or "",
            height=400,
            key="edited_strategy"
        )
        
        # Save buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Cancel"):
                st.session_state.page = "generate_strategy"
                st.rerun()
        
        with col2:
            if st.button("Save Changes", type="primary"):
                campaign.strategy = edited_strategy
                st.success("Strategy updated successfully!")
                st.session_state.page = "generate_deliverables"
                st.rerun()

def sidebar_navigation():
    """Sidebar navigation"""
    st.sidebar.title("Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    if st.sidebar.button("📊 Analytics"):
        st.session_state.page = "analytics"
        st.rerun()
    
    if st.sidebar.button("⚙️ Settings"):
        st.session_state.page = "settings"
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Campaign quick access
    if st.session_state.campaigns:
        st.sidebar.markdown("### Quick Access")
        for campaign_id, campaign in st.session_state.campaigns.items():
            if st.sidebar.button(f"📋 {campaign.name[:20]}...", key=f"quick_{campaign_id}"):
                st.session_state.current_campaign = campaign_id
                st.session_state.page = "view_campaign"
                st.rerun()

def analytics_page():
    """Analytics dashboard"""
    st.title("📊 Analytics Dashboard")
    
    # Overall metrics
    st.markdown("### Overall Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Campaigns", len(st.session_state.campaigns))
    with col2:
        st.metric("Success Rate", "78%")
    with col3:
        st.metric("Avg ROI", "3.4x")
    with col4:
        st.metric("Total Reach", "2.1M")
    
    # Performance by industry
    st.markdown("### Performance by Industry")
    
    # Sample data
    industry_data = pd.DataFrame({
        'Industry': ['E-commerce', 'SaaS', 'Consumer Goods', 'Education', 'Health & Wellness'],
        'Campaigns': [15, 8, 12, 6, 9],
        'Avg ROI': [3.2, 4.1, 2.8, 3.9, 3.5],
        'Success Rate': [85, 75, 80, 90, 82]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_roi = px.bar(industry_data, x='Industry', y='Avg ROI', 
                        title='Average ROI by Industry')
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        fig_success = px.bar(industry_data, x='Industry', y='Success Rate', 
                           title='Success Rate by Industry')
        st.plotly_chart(fig_success, use_container_width=True)
    
    # Trend analysis
    st.markdown("### Campaign Trends")
    
    # Sample trend data
    trend_data = pd.DataFrame({
        'Month': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Campaigns Created': [5, 8, 12, 15, 18, 22, 25, 30, 28, 32, 35, 38],
        'Avg Performance': [2.1, 2.3, 2.8, 3.1, 3.4, 3.2, 3.6, 3.8, 3.5, 3.9, 4.1, 4.2]
    })
    
    fig_trend = px.line(trend_data, x='Month', y=['Campaigns Created', 'Avg Performance'], 
                       title='Campaign Creation and Performance Trends')
    st.plotly_chart(fig_trend, use_container_width=True)

def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    
    # API Configuration
    st.markdown("### API Configuration")
    
    with st.expander("Azure OpenAI Settings"):
        azure_base_url = st.text_input("Azure OpenAI Base URL", 
                                     value=os.getenv("AZURE_OPENAI_API_BASE", ""))
        azure_api_key = st.text_input("Azure OpenAI API Key", 
                                    value="*" * 20 if os.getenv("AZURE_OPENAI_API_KEY", "") else "",
                                    type="password")
        deployment_name = st.text_input("Deployment Name", value=os.getenv("DEPLOYMENT_NAME", ""))
        
        # openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE", "azure")
        #     openai.api_base = os.getenv("AZURE_OPENAI_API_BASE", "")
        #     openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        #     openai.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        #     openai.deployment = os.getenv("DEPLOYMENT_NAME", "")
        if st.button("Test Connection"):
            st.success("✅ Connection successful!")
    
    # Default Settings
    st.markdown("### Default Campaign Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_industry = st.selectbox("Default Industry", 
                                      ["E-commerce", "SaaS", "Consumer Goods", "Entertainment", "Education"])
        default_budget = st.selectbox("Default Budget Range", 
                                    ["$1,000 - $5,000", "$5,000 - $15,000", "$15,000 - $50,000"])
    
    with col2:
        default_duration = st.selectbox("Default Campaign Duration", 
                                      ["2 weeks", "1 month", "3 months", "6 months"])
        default_goal = st.selectbox("Default Primary Goal", 
                                  ["Brand Awareness", "Lead Generation", "Sales Conversion"])
    
    # Notification Settings
    st.markdown("### Notification Settings")
    
    email_notifications = st.checkbox("Email Notifications", value=True)
    performance_alerts = st.checkbox("Performance Alerts", value=True)
    weekly_reports = st.checkbox("Weekly Reports", value=False)
    
    # Export Settings
    st.markdown("### Export Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Default Export Format", ["PDF", "CSV", "Excel"])
    
    with col2:
        include_charts = st.checkbox("Include Charts in Reports", value=True)
    
    # Save settings
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Main application logic
def main():
    """Main application entry point"""
    
    # if 'page' not in st.session_state:
    #     st.session_state.page = "dashboard"
    # Initialize session state and load data
    initialize_session_state()

        # Initialize other session state variables
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = {}
    if 'current_campaign' not in st.session_state:
        st.session_state.current_campaign = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    # # Auto-save campaigns periodically
    if st.session_state.campaigns:
        save_campaigns_to_file(st.session_state.campaigns)
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Main content based on current page
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "create_campaign":
        create_campaign_page_improved()
    elif st.session_state.page == "generate_strategy":
        generate_strategy_page()
    elif st.session_state.page == "edit_strategy":
        edit_strategy_page()
    elif st.session_state.page == "generate_deliverables":
        generate_deliverables_page()
    elif st.session_state.page == "view_campaign":
        view_campaign_page()
    elif st.session_state.page == "analytics":
        analytics_page()
    elif st.session_state.page == "settings":
        settings_page()
    
    # Footer
    st.markdown("---")
    st.markdown("*Marketing Campaign Agent - Powered by AI*")

if __name__ == "__main__":
    main()

# Additional utility functions

def validate_campaign_data(sostac_data: Dict) -> bool:
    """Validate campaign data before processing"""
    required_fields = [
        ('situation', 'industry'),
        ('objectives', 'primary_goal'),
        ('objectives', 'budget_range'),
        ('strategy', 'target_audience')
    ]
    
    for section, field in required_fields:
        if not sostac_data.get(section, {}).get(field):
            return False
    
    return True

def generate_campaign_summary(campaign: Campaign) -> Dict:
    """Generate a summary of campaign key metrics"""
    summary = {
        "name": campaign.name,
        "status": "Approved" if campaign.approved else "Draft",
        "industry": campaign.sostac_data.get('situation', {}).get('industry', 'N/A'),
        "budget": campaign.sostac_data.get('objectives', {}).get('budget_range', 'N/A'),
        "duration": campaign.sostac_data.get('objectives', {}).get('campaign_duration', 'N/A'),
        "channels": campaign.sostac_data.get('tactics', {}).get('channels', []),
        "target_audience": campaign.sostac_data.get('strategy', {}).get('target_audience', 'N/A'),
        "created_at": campaign.created_at
    }
    
    return summary

def calculate_campaign_score(campaign: Campaign) -> float:
    """Calculate a quality score for the campaign"""
    score = 0
    
    # Check completeness
    if campaign.strategy:
        score += 30
    if campaign.deliverables:
        score += 30
    if campaign.influencers:
        score += 20
    if campaign.approved:
        score += 20
    
    return score

def get_campaign_recommendations(campaign: Campaign) -> List[str]:
    """Get recommendations for improving campaign"""
    recommendations = []
    
    if not campaign.strategy:
        recommendations.append("Generate a comprehensive strategy")
    
    if not campaign.deliverables:
        recommendations.append("Create detailed deliverables")
    
    if not campaign.influencers:
        recommendations.append("Identify relevant influencers")
    
    # Check budget allocation
    budget = campaign.sostac_data.get('objectives', {}).get('budget_range', '')
    if 'low' in budget.lower():
        recommendations.append("Consider increasing budget for better reach")
    
    # Check channel diversity
    channels = campaign.sostac_data.get('tactics', {}).get('channels', [])
    if len(channels) < 3:
        recommendations.append("Consider diversifying marketing channels")
    
    return recommendations

# Performance tracking functions
def track_campaign_performance(campaign_id: str) -> Dict:
    """Track campaign performance metrics"""
    # This would integrate with actual analytics platforms
    
    # Sample performance data
    performance = {
        "impressions": 125000,
        "clicks": 8500,
        "conversions": 342,
        "ctr": 6.8,
        "conversion_rate": 4.0,
        "cost_per_click": 1.25,
        "cost_per_conversion": 31.50,
        "roi": 3.2,
        "engagement_rate": 5.4,
        "reach": 89000
    }
    
    return performance

def generate_performance_report(campaign: Campaign) -> str:
    """Generate a comprehensive performance report"""
    performance = track_campaign_performance(campaign.name)
    
    report = f"""
    # Campaign Performance Report
    
    ## Campaign: {campaign.name}
    
    ### Key Metrics
    - **Impressions**: {performance['impressions']:,}
    - **Clicks**: {performance['clicks']:,}
    - **Conversions**: {performance['conversions']:,}
    - **CTR**: {performance['ctr']}%
    - **Conversion Rate**: {performance['conversion_rate']}%
    - **ROI**: {performance['roi']}x
    
    ### Analysis
    This campaign is performing {"above" if performance['roi'] > 3 else "below"} expectations
    with a {performance['roi']}x return on investment.
    
    ### Recommendations
    - Optimize high-performing ad creatives
    - Increase budget allocation to top-performing channels
    - A/B test new messaging approaches
    """
    
    return report

# Integration functions for external APIs
def integrate_google_analytics(campaign_id: str) -> Dict:
    """Integrate with Google Analytics for real-time data"""
    # This would use the Google Analytics API
    # For now, return sample data
    
    return {
        "sessions": 15420,
        "page_views": 34567,
        "bounce_rate": 34.2,
        "avg_session_duration": 245,
        "goal_completions": 1234,
        "conversion_rate": 8.0
    }

def integrate_social_media_apis(campaign_id: str) -> Dict:
    """Integrate with social media APIs for performance data"""
    # This would integrate with Facebook, Instagram, Twitter APIs
    
    return {
        "facebook": {
            "reach": 45000,
            "engagement": 3450,
            "clicks": 1234
        },
        "instagram": {
            "reach": 38000,
            "engagement": 2890,
            "clicks": 987
        },
        "twitter": {
            "impressions": 67000,
            "engagement": 1234,
            "clicks": 456
        }
    }

def schedule_campaign_posts(campaign: Campaign) -> bool:
    """Schedule social media posts based on campaign strategy"""
    # This would integrate with scheduling tools like Hootsuite, Buffer
    
    # Extract posting schedule from strategy
    if campaign.deliverables and 'social_media_calendar' in campaign.deliverables:
        # Schedule posts
        st.success("Posts scheduled successfully!")
        return True
    
    return False