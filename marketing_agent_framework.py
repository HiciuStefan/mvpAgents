import streamlit as st
import openai
from datetime import datetime, timedelta
import json
import pandas as pd
import requests
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
import time
import os
from dotenv import load_dotenv

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

@dataclass
class Campaign:
    name: str
    sostac_data: Dict
    strategy: Optional[str] = None
    deliverables: Optional[Dict] = None
    influencers: Optional[List] = None
    approved: bool = False
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class MarketingAgent:
    def __init__(self):
        self.azure_client = None
        self.init_azure_client()
    
    def init_azure_client(self):
        """Initialize Azure OpenAI client"""
        try:
            # You'll need to set these in your environment or Streamlit secrets
            openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE", "azure")
            openai.api_base = os.getenv("AZURE_OPENAI_API_BASE", "")
            openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
            openai.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
            openai.deployment = os.getenv("DEPLOYMENT_NAME", "")
            self.azure_client = openai
        except Exception as e:
            st.error(f"Azure OpenAI setup error: {e}")
    
    def get_trending_topics(self, country: str = "US") -> List[str]:
        """Get trending topics using Google Trends API or similar"""
        # This is a placeholder - you'd integrate with actual trending APIs
        sample_trends = [
            "AI automation", "sustainable lifestyle", "remote work tools",
            "health tech", "e-commerce growth", "digital transformation",
            "social media marketing", "customer experience", "data privacy"
        ]
        return sample_trends[:5]
    
    def analyze_competitors(self, industry: str, competitors: List[str]) -> Dict:
        """Analyze competitor campaigns and strategies"""
        # This would integrate with web scraping tools
        competitor_analysis = {
            "messaging_gaps": [
                "Lack of sustainability focus",
                "Missing mobile-first approach",
                "No personalization strategy"
            ],
            "content_opportunities": [
                "Video content underutilized",
                "User-generated content potential",
                "Influencer partnerships gaps"
            ],
            "positioning_gaps": [
                "Premium market positioning available",
                "Niche audience underserved",
                "Geographic expansion opportunities"
            ]
        }
        return competitor_analysis
    
    def generate_campaign_strategy(self, sostac_data: Dict, trends: List[str], competitor_analysis: Dict) -> str:
        """Generate comprehensive campaign strategy using LLM"""
        
        system_prompt = """
        You are an expert B2C marketing strategist specializing in creating comprehensive campaign strategies.
        Use the SOSTAC framework analysis, current trends, and competitor insights to create a detailed campaign strategy.
        
        Focus on:
        - Strategic positioning and messaging
        - Channel selection and timing
        - Content themes and formats
        - Budget allocation recommendations
        - Timeline with key milestones
        - Success metrics and KPIs
        
        Provide a structured, actionable strategy that can be implemented immediately.
        """
        
        user_prompt = f"""
        Create a comprehensive B2C marketing campaign strategy based on:
        
        SOSTAC Analysis:
        {json.dumps(sostac_data, indent=2)}
        
        Current Trends to Leverage:
        {', '.join(trends)}
        
        Competitor Analysis:
        {json.dumps(competitor_analysis, indent=2)}
        
        Provide a detailed strategy with:
        1. Executive Summary
        2. Strategic Positioning
        3. Target Audience Segments
        4. Key Messages by Segment
        5. Channel Strategy & Timeline
        6. Content Calendar Overview
        7. Budget Allocation
        8. Success Metrics
        9. Risk Mitigation
        10. Next Steps
        """
        
        try:
            response = self.azure_client.ChatCompletion.create(
                engine="gpt-4",  # Replace with your deployment name
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating strategy: {e}"
    
    def generate_deliverables(self, strategy: str, sostac_data: Dict) -> Dict:
        """Generate specific deliverables based on approved strategy"""
        
        system_prompt = """
        You are a marketing execution specialist. Based on the approved campaign strategy,
        generate specific, actionable deliverables for B2C campaigns.
        
        Create detailed deliverables including:
        - Email sequences with subject lines and content
        - Landing page structures with copy
        - Social media content calendars
        - Ad copy variations
        - Influencer collaboration briefs
        - Webinar structures if applicable
        
        Make everything actionable and ready for implementation.
        """
        
        user_prompt = f"""
        Based on this approved strategy:
        {strategy}
        
        And SOSTAC data:
        {json.dumps(sostac_data, indent=2)}
        
        Generate detailed deliverables for:
        1. Email Marketing Sequence (3-5 emails)
        2. Landing Page Structure & Copy
        3. Social Media Content Calendar (2 weeks)
        4. Ad Copy Variations (3-5 versions)
        5. Influencer Collaboration Brief
        6. Performance Tracking Setup
        
        Format as JSON with clear sections for each deliverable.
        """
        
        try:
            response = self.azure_client.ChatCompletion.create(
                engine="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"Error generating deliverables: {e}"}
    
    def find_influencers(self, industry: str, country: str, budget_range: str) -> List[Dict]:
        """Find relevant influencers based on campaign parameters"""
        # This would integrate with influencer databases
        sample_influencers = [
            {
                "name": "Sarah Johnson",
                "platform": "Instagram",
                "followers": "250K",
                "engagement_rate": "4.2%",
                "niche": industry,
                "estimated_cost": "$2,500-$5,000",
                "country": country,
                "recent_performance": "High engagement on product reviews"
            },
            {
                "name": "Mike Chen",
                "platform": "TikTok",
                "followers": "180K",
                "engagement_rate": "6.8%",
                "niche": industry,
                "estimated_cost": "$1,500-$3,000",
                "country": country,
                "recent_performance": "Viral content creator"
            },
            {
                "name": "Emma Rodriguez",
                "platform": "YouTube",
                "followers": "95K",
                "engagement_rate": "3.5%",
                "niche": industry,
                "estimated_cost": "$3,000-$6,000",
                "country": country,
                "recent_performance": "Long-form content specialist"
            }
        ]
        return sample_influencers

# SOSTAC Framework Questions
SOSTAC_QUESTIONS = {
    "situation": {
        "title": "Situation Analysis",
        "questions": [
            {
                "question": "What type of business are you marketing?",
                "type": "radio",
                "options": ["Product", "Service", "Both"],
                "key": "business_type"
            },
            {
                "question": "What industry are you in?",
                "type": "selectbox",
                "options": ["E-commerce", "SaaS", "Consumer Goods", "Entertainment", "Education", "Health & Wellness", "Fashion", "Food & Beverage", "Travel", "Other"],
                "key": "industry"
            },
            {
                "question": "Describe your current market position",
                "type": "text_area",
                "key": "market_position"
            },
            {
                "question": "Who are your main competitors? (separate by commas)",
                "type": "text_input",
                "key": "competitors"
            },
            {
                "question": "What's your current market share?",
                "type": "selectbox",
                "options": ["Market Leader (>40%)", "Strong Position (20-40%)", "Moderate Share (10-20%)", "Small Share (<10%)", "New Entrant"],
                "key": "market_share"
            },
            {
                "question": "What are your main business challenges?",
                "type": "multiselect",
                "options": ["Low brand awareness", "High competition", "Customer acquisition cost", "Customer retention", "Market saturation", "Seasonal fluctuations", "Limited budget"],
                "key": "challenges"
            }
        ]
    },
    "objectives": {
        "title": "Objectives & Goals",
        "questions": [
            {
                "question": "What's your primary campaign goal?",
                "type": "radio",
                "options": ["Brand Awareness", "Lead Generation", "Sales Conversion", "Customer Retention", "Market Expansion"],
                "key": "primary_goal"
            },
            {
                "question": "What's your campaign budget range?",
                "type": "selectbox",
                "options": ["$1,000 - $5,000", "$5,000 - $15,000", "$15,000 - $50,000", "$50,000 - $100,000", "$100,000+"],
                "key": "budget_range"
            },
            {
                "question": "How long do you want your campaign to run?",
                "type": "selectbox",
                "options": ["2 weeks", "1 month", "3 months", "6 months", "Ongoing"],
                "key": "campaign_duration"
            },
            {
                "question": "What's your target ROI expectation?",
                "type": "selectbox",
                "options": ["2x", "3x", "4x", "5x+", "Not sure"],
                "key": "target_roi"
            },
            {
                "question": "Which metrics matter most to you?",
                "type": "multiselect",
                "options": ["Website Traffic", "Lead Quality", "Conversion Rate", "Brand Mentions", "Social Engagement", "Email Open Rates", "Customer Lifetime Value"],
                "key": "key_metrics"
            }
        ]
    },
    "strategy": {
        "title": "Strategy & Positioning",
        "questions": [
            {
                "question": "Who is your primary target audience?",
                "type": "text_area",
                "key": "target_audience"
            },
            {
                "question": "What age group are you targeting?",
                "type": "multiselect",
                "options": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                "key": "age_groups"
            },
            {
                "question": "What's your unique value proposition?",
                "type": "text_area",
                "key": "value_proposition"
            },
            {
                "question": "What's your brand personality?",
                "type": "multiselect",
                "options": ["Professional", "Friendly", "Innovative", "Trustworthy", "Fun", "Luxurious", "Accessible", "Bold"],
                "key": "brand_personality"
            },
            {
                "question": "What emotional response do you want to evoke?",
                "type": "multiselect",
                "options": ["Trust", "Excitement", "Comfort", "Urgency", "Aspiration", "Security", "Joy", "Pride"],
                "key": "emotional_response"
            }
        ]
    },
    "tactics": {
        "title": "Tactics & Channels",
        "questions": [
            {
                "question": "Which marketing channels do you want to use?",
                "type": "multiselect",
                "options": ["Social Media", "Email Marketing", "Content Marketing", "PPC Advertising", "SEO", "Influencer Marketing", "Video Marketing", "Webinars"],
                "key": "channels"
            },
            {
                "question": "What's your preferred social media platforms?",
                "type": "multiselect",
                "options": ["Instagram", "Facebook", "TikTok", "YouTube", "LinkedIn", "Twitter", "Pinterest", "Snapchat"],
                "key": "social_platforms"
            },
            {
                "question": "What type of content resonates with your audience?",
                "type": "multiselect",
                "options": ["Educational", "Entertainment", "Behind-the-scenes", "User-generated", "Product demos", "Testimonials", "Trends/News", "Inspirational"],
                "key": "content_types"
            },
            {
                "question": "What's your content creation capacity?",
                "type": "radio",
                "options": ["High (Daily posts)", "Medium (2-3 times/week)", "Low (Weekly)", "Very Low (Bi-weekly)"],
                "key": "content_capacity"
            }
        ]
    },
    "actions": {
        "title": "Actions & Implementation",
        "questions": [
            {
                "question": "What's your team size for this campaign?",
                "type": "selectbox",
                "options": ["Just me", "2-3 people", "4-6 people", "7-10 people", "10+ people"],
                "key": "team_size"
            },
            {
                "question": "What tools do you currently use?",
                "type": "multiselect",
                "options": ["Google Analytics", "Facebook Ads", "Mailchimp", "HubSpot", "Hootsuite", "Canva", "Figma", "Slack", "None"],
                "key": "current_tools"
            },
            {
                "question": "When do you want to launch?",
                "type": "selectbox",
                "options": ["Immediately", "Within 1 week", "Within 2 weeks", "Within 1 month", "Specific date"],
                "key": "launch_timing"
            }
        ]
    },
    "control": {
        "title": "Control & Measurement",
        "questions": [
            {
                "question": "How often do you want to review campaign performance?",
                "type": "radio",
                "options": ["Daily", "Weekly", "Bi-weekly", "Monthly"],
                "key": "review_frequency"
            },
            {
                "question": "What's your tolerance for campaign adjustments?",
                "type": "radio",
                "options": ["High - Adjust frequently", "Medium - Adjust weekly", "Low - Adjust monthly", "Very Low - Minimal adjustments"],
                "key": "adjustment_tolerance"
            },
            {
                "question": "What would you consider campaign success?",
                "type": "text_area",
                "key": "success_definition"
            }
        ]
    }
}

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

def collect_sostac_data() -> Dict:
    """Collect all SOSTAC responses from session state"""
    sostac_data = {}
    for section, section_data in SOSTAC_QUESTIONS.items():
        sostac_data[section] = {}
        for question in section_data["questions"]:
            key = f"{section}_{question['key']}"
            sostac_data[section][question['key']] = st.session_state.get(key, "")
    return sostac_data

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

def create_campaign_page():
    """Multi-step campaign creation process"""
    st.title("🎯 Create New Campaign")
    
    # Progress indicator
    steps = ["Basic Info", "Situation", "Objectives", "Strategy", "Tactics", "Actions", "Control", "Review"]
    current_step = st.session_state.current_step
    
    # Progress bar
    progress = (current_step + 1) / len(steps)
    st.progress(progress)
    
    # Step indicator
    st.markdown(f"**Step {current_step + 1} of {len(steps)}: {steps[current_step]}**")
    
    if current_step == 0:
        # Basic campaign info
        st.markdown("### Campaign Information")
        
        campaign_name = st.text_input("Campaign Name", key="campaign_name")
        campaign_description = st.text_area("Campaign Description (Optional)", key="campaign_description")
        
        if st.button("Next", disabled=not campaign_name):
            st.session_state.current_step = 1
            st.rerun()
    
    elif current_step in [1, 2, 3, 4, 5, 6]:
        # SOSTAC questions
        section_keys = list(SOSTAC_QUESTIONS.keys())
        section_key = section_keys[current_step - 1]
        section_data = SOSTAC_QUESTIONS[section_key]
        
        st.markdown(f"### {section_data['title']}")
        
        # Render questions for this section
        for question in section_data["questions"]:
            render_question(question, section_key)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous") and current_step > 0:
                st.session_state.current_step -= 1
                st.rerun()
        
        with col2:
            if st.button("Next"):
                st.session_state.current_step += 1
                st.rerun()
    
    elif current_step == 7:
        # Review and create campaign
        st.markdown("### Review Your Campaign")
        
        # Collect all data
        sostac_data = collect_sostac_data()
        campaign_name = st.session_state.get("campaign_name", "")
        
        # Display summary
        st.markdown("#### Campaign Summary")
        st.write(f"**Name:** {campaign_name}")
        st.write(f"**Industry:** {sostac_data.get('situation', {}).get('industry', 'N/A')}")
        st.write(f"**Primary Goal:** {sostac_data.get('objectives', {}).get('primary_goal', 'N/A')}")
        st.write(f"**Budget:** {sostac_data.get('objectives', {}).get('budget_range', 'N/A')}")
        st.write(f"**Duration:** {sostac_data.get('objectives', {}).get('campaign_duration', 'N/A')}")
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous"):
                st.session_state.current_step -= 1
                st.rerun()
        
        with col2:
            if st.button("Create Campaign", type="primary"):
                # Create campaign
                campaign_id = f"campaign_{len(st.session_state.campaigns) + 1}"
                campaign = Campaign(
                    name=campaign_name,
                    sostac_data=sostac_data
                )
                st.session_state.campaigns[campaign_id] = campaign
                st.session_state.current_campaign = campaign_id
                st.session_state.page = "generate_strategy"
                st.rerun()

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
                                     value=st.secrets.get("AZURE_OPENAI_BASE_URL", ""))
        azure_api_key = st.text_input("Azure OpenAI API Key", 
                                    value="*" * 20 if st.secrets.get("AZURE_OPENAI_API_KEY") else "",
                                    type="password")
        deployment_name = st.text_input("Deployment Name", value="gpt-4")
        
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

def export_campaign_data():
    """Export campaign data to various formats"""
    if st.session_state.current_campaign:
        campaign = st.session_state.campaigns[st.session_state.current_campaign]
        
        # Create export data
        export_data = {
            "Campaign Name": campaign.name,
            "Created": campaign.created_at,
            "Status": "Approved" if campaign.approved else "Draft",
            "Industry": campaign.sostac_data.get('situation', {}).get('industry', 'N/A'),
            "Budget": campaign.sostac_data.get('objectives', {}).get('budget_range', 'N/A'),
            "Duration": campaign.sostac_data.get('objectives', {}).get('campaign_duration', 'N/A'),
            "Primary Goal": campaign.sostac_data.get('objectives', {}).get('primary_goal', 'N/A'),
            "Strategy": campaign.strategy or "Not generated",
            "Deliverables": str(campaign.deliverables) if campaign.deliverables else "Not generated"
        }
        
        # Convert to DataFrame for CSV export
        df = pd.DataFrame([export_data])
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"{campaign.name}_export.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"{campaign.name}_export.json",
                mime="application/json"
            )
        
        with col3:
            # For PDF, we'd need additional libraries
            st.info("PDF export coming soon!")

# Main application logic
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Main content based on current page
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "create_campaign":
        create_campaign_page()
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