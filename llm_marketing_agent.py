from itertools import count
import json
from typing import Any, Dict, List, Optional
import os
import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, SecretStr, ValidationError
from pytrends.request import TrendReq

from find_influencers import YouTubeInfluencerFinder

load_dotenv()

class MarketingAgent:
    def __init__(self):
        self.azure_client = None
        self.init_azure_client()
    
    def init_azure_client(self):
        """Initialize Azure OpenAI client"""
        try:
            # You'll need to set these in your environment or Streamlit secrets
            endpoint = os.getenv("AZURE_OPENAI_API_BASE")
            subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
            version=os.getenv("AZURE_OPENAI_API_VERSION")
            deployment = os.getenv("DEPLOYMENT_NAME")
           
            self.azure_client =  AzureChatOpenAI(
                azure_endpoint   = endpoint,   
                api_key          = SecretStr(subscription_key) if subscription_key else None,
                api_version      = version,
                azure_deployment = deployment, 
                temperature =   0.3,
            )
        except Exception as e:
            st.error(f"Azure OpenAI setup error: {e}")
    
    def get_trending_topics(self, keywords: list) -> Dict[str, Any]:
        """Get trending topics using Google Trends API or similar"""
        pytrends = TrendReq(hl='en-US', tz=0,retries=3, backoff_factor=0.5)
        
        # Check if keywords are provided
        if not keywords:
            st.error("No keywords provided for trending topics.")
            return ""
        if not isinstance(keywords, list):
            st.error("Keywords should be provided as a list.")
            return ""
        
        # Validate keywords
        for keyword in keywords:
            if not isinstance(keyword, str) or not keyword.strip():
                st.error(f"Invalid keyword: {keyword}. Keywords should be non-empty strings.")
                return ""
            
        # Ensure keywords are in lowercase
        keywords = [keyword.lower().strip() for keyword in keywords if isinstance(keyword, str) and keyword.strip()]
        if not keywords:
            st.error("No valid keywords provided for trending topics.")
            return ""
        
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=60)

        # Convert dates to string format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Build the payload for one or more search terms
        pytrends.build_payload(
        kw_list = keywords,  # list of queries (Romanian for “artificial intelligence”)
        timeframe = f'{start_date_str} {end_date_str}',#'now 7-d',                   # last 7 days
        geo='RO',                                # blank = world; use country codes (e.g. 'RO')
        )

        # Get interest over time
        interest_over_time_df = pytrends.interest_over_time()

        # Resample the data to get monthly values
        if interest_over_time_df.empty:
            st.error("No data found for the provided keywords.")
            return []
        
        # 2. Interest over time monthly
        monthly_total_interest_df = (
            interest_over_time_df
                .resample('M')
                .sum()
                .reset_index() 
                .rename(columns={interest_over_time_df.index.name or 'date': 'month'})
            )

        # 3. Today's trending searches in Romania
        trending_df = pytrends.trending_searches(pn='romania')
        # The result is a single-column DataFrame; grab top 10 as list
        trending_searches = trending_df[0].head(10).tolist()

        # 4. Related topics (higher-level clusters)
        topics_dict = pytrends.related_topics().get(keyword, {})
        top_topics_df = topics_dict.get('top')
        related_topics = (
            top_topics_df.reset_index()
            .rename(columns={'topic_title':'topic', 'value':'score'})
            .to_dict(orient='records')
        ) if top_topics_df is not None else []

        # 5. Related queries (exact search phrases)
        queries_dict = pytrends.related_queries().get(keyword, {})
        top_q_df    = queries_dict.get('top')
        rising_q_df = queries_dict.get('rising')

        top_queries    = top_q_df.to_dict(orient='records')    if top_q_df    is not None else []
        rising_queries = rising_q_df.to_dict(orient='records') if rising_q_df is not None else []

        return {
            'monthly_total_interest': monthly_total_interest_df,
            'trending_searches': trending_searches,
            'related_topics': related_topics,
            'top_queries': top_queries,
            'rising_queries': rising_queries
        }

    
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
    
    def generate_campaign_strategy(self, sostac_data: Dict, trends: Dict, competitor_analysis: List[str]) -> str:
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
        {json.dumps(trends, indent=2)}
        
        Competitors:
        {', '.join(competitor_analysis)}
        
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
        10.Top 3 thematic hooks for a marketing campaign.
        """
        
        try:
            message = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            if not self.azure_client:
                return "Azure OpenAI client is not initialized."
            response = self.azure_client.invoke(message)
                              
            
            return str(response.content)
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
            if not self.azure_client:
                return {"error": "Azure OpenAI client is not initialized."}
            message = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            response = self.azure_client.invoke(message)
            return json.loads(str(response.content))
        except Exception as e:
            return {"error": f"Error generating deliverables: {e}"}
    
    def find_influencers(self, industry: str, country: str, budget_range: str) -> List[Dict]:
        """Find relevant influencers based on campaign parameters"""
        finder = YouTubeInfluencerFinder("YOUR_YOUTUBE_API_KEY")
        influencers = finder.find_influencers(
            industry=industry,
            country=country, 
            budget_range=budget_range
        )
        if not influencers:
            st.error("No influencers found for the specified criteria.")
            return []
        return influencers

