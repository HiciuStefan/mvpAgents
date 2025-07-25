from itertools import count
import json
from typing import Any, Dict, List, Optional
import os
import streamlit as st
import os
import datetime
import html
import re
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
        #trending_df = pytrends.trending_searches()
        # The result is a single-column DataFrame; grab top 10 as list
        #trending_searches = trending_df[0].head(10).tolist()

        # 4. Related topics (higher-level clusters)
        # topics_dict = pytrends.related_topics().get(keyword, {})
        # top_topics_df = topics_dict.get('top')
        # related_topics = (
        #     top_topics_df.reset_index()
        #     .rename(columns={'topic_title':'topic', 'value':'score'})
        #     .to_dict(orient='records')
        # ) if top_topics_df is not None else []

        # 5. Related queries (exact search phrases)
        # queries_dict = pytrends.related_queries().get(keyword, {})
        # top_q_df    = queries_dict.get('top')
        # rising_q_df = queries_dict.get('rising')

        # top_queries    = top_q_df.to_dict(orient='records')    if top_q_df    is not None else []
        # rising_queries = rising_q_df.to_dict(orient='records') if rising_q_df is not None else []

        trending_searches={
        #     'monthly_total_interest': monthly_total_interest_df,
        #    # 'trending_searches': trending_searches,
        # #    'related_topics': related_topics,
        #     'top_queries': top_queries,
        #     'rising_queries': rising_queries
        }

        print("Trending keywords:", keywords)
      #  print("Trending searches data:", trending_searches)

        return trending_searches
    
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
    
    def generate_campaign_strategy(self, sostac_data: Dict, trends: Dict, competitor_analysis: List[str]) -> Dict:
        """Generate comprehensive campaign strategy using LLM"""
        
        objectives = sostac_data.get('objectives', {})
        
        budget_range = objectives.get('budget_range', '')
        campaign_duration = objectives.get('campaign_duration', '')
        target_roi = objectives.get('target_roi', '')
        key_metrics= ", ".join(objectives.get("key_metrics", []))

        strategy = sostac_data.get('strategy', {})
        
        brand_personality = ", ".join(strategy.get("brand_personality", []))
        emotional_response = ", ".join(strategy.get("emotional_response", []))

        system_prompt = f"""
        You are a B2C marketing strategist and copywriter.  
        Using the inputs provided, cover these strategic dimensions wherever data exists:
        1. Strategic Positioning  
        2. Target Audience Segments  
        3. Key Messages by Segment  
        4. Channel Strategy & Timeline  
        5. Content Calendar Overview  
        6. Budget Allocation  
        7. Success Metrics & KPIs  
        8. Risk Mitigation & Contingency Plan  
        9. Top 3 Thematic Hooks  

        Produce one valid JSON object with two keys:

        • "strategy":  
            - A JSON-friendly dict (key:value) for each of the above sections—omit any section with no input data.  
            - Each section: 2-3 sentences for strategic rationales and concise bullet for tactical steps.  

        • "markdown":  
            - A human-readable Markdown document using the exact heading hierarchy:  
                # Executive Summary  
                ## 1. Strategic Positioning  
                ## 2. Target Audience Segments  
                …  
                ## 9. Top 3 Thematic Hooks  
            - Omit any heading that has no content (i.e., no input data). 
            - Under each heading: 1-2 sentence “Why” tying it back to the inputs, then bullets for actions.


        Respect these constraints:  
        - Total budget: {budget_range}  
        - Campaign duration: {campaign_duration}  
        - Target ROI: {target_roi}  

        Return **only** the JSON—no extra text, no code fences.
        """

        user_prompt = f"""
        Here are your inputs:

        SOSTAC Data:
        {json.dumps(sostac_data, indent=2)}

        Current Trends:
        {json.dumps(trends, indent=2)}

        # Competitors:
        # {', '.join(competitor_analysis)}

        Brand Personality: {brand_personality}
        Emotional Response:  {emotional_response}
        Value Proposition:   {strategy.get('value_proposition',{})}
        Key Metrics:         {key_metrics}

        Now generate the JSON outlined in the system instructions above.
        """
        
        try:
            message = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

            print("Generating strategy with message:")
            if not self.azure_client:
                return "Azure OpenAI client is not initialized."
            response = self.azure_client.invoke(message)
            return json.loads(response.content)
        
        except Exception as e:
            return f"Error generating strategy: {e}"
    
    def generate_deliverables(self, approved_strategy: Dict[str, any]) -> str:
        """Generate specific deliverables based on approved strategy"""

        system_prompt = """
            You are a Marketing Execution Specialist with a knack for turning approved strategies into turnkey campaigns. 
            You have in front of you an APPROVED campaign strategy in JSON format.
            Your job: Produce ONLY the execution-ready marketing assets **called for by that strategy**—no extras, no fluff.

            For each asset you generate, include:
            - A clear, descriptive title in this format:
              [Channel] – [Primary Audience or Benefit Hook] – [Action]
            - A brief “Why” tying it to the strategy (e.g. “Supports lead generation goal”)
            - Full copy or templates/structure (emails, ads, social posts, etc) keeping in mind brand personality and emotional response
            - Timeline or schedule (dates or sequence slots)
            - Call-to-Action (what the audience should do next)
            - Primary KPI(s) to measure success
            - Constraints: honor the budget, duration, and ROI limits from the strategy

            Return your output in plain Markdown, with headings and sub-headings. No code fences, no JSON. Do not use any emojis, Unicode symbols, or special characters. Only use standard English letters, numbers, and basic punctuation (.,!?-).
            """

        user_prompt = f"""
            Here is the APPROVED strategy:

            {approved_strategy}

            Only generate the assets the strategy explicitly or implicitly demands.  
            """
        try:
            if not self.azure_client:
                return {"error": "Azure OpenAI client is not initialized."}
            message = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            
            response = self.azure_client.invoke(message)
            # print("Response from Azure OpenAI:", response)
            sanitized_resp=self.sanitize_llm_output(response.content)
            return sanitized_resp
        
        except Exception as e:
            return {"error": f"Error generating deliverables: {e}"}
    
    def strip_code_fences(self, text: str) -> str:
        lines = text.strip().splitlines()
        if lines and lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1]).strip()
        return text.strip()
    
    def decode_entities(self, text: str) -> str:
        # return html.unescape(text.encode('utf-8').decode('unicode_escape'))
        # return text.encode("latin-1").decode("utf-8")
        return html.unescape(text)

    
    def collapse_whitespace(self, text: str) -> str:
        lines = [line.rstrip() for line in text.strip().splitlines()]
        return "\n".join(lines)

    def fix_numbered_list(self, text: str) -> str:
        return text.replace("1)", "1.").replace("2)", "2.").replace("3)", "3.")
    
    def sanitize_llm_output(self, text: str) -> str:
        text = self.strip_code_fences(text)
        text = self.decode_entities(text)
        text = self.collapse_whitespace(text)
        text = self.fix_numbered_list(text)
        return text
    
    def parse_markdown_sections(self,md: str) -> List[Dict]:
        """
        Splits a Markdown string into sections at headings (#, ##, ###).
        Returns a list of dicts: { level: int, title: str|None, content: str }.
        - level:   0 for the global intro, 1 for '#', 2 for '##', 3 for '###'
        - title:   the heading text (None for the intro)
        - content: everything up until the next heading
        """
        # Normalize line endings
        md = md.replace('\r\n', '\n').rstrip()
        
        # Find all headings of level 1–3
        pattern = re.compile(r'^(?P<hashes>#{1,3})\s+(?P<title>.+)', re.MULTILINE)
        matches = list(pattern.finditer(md))
        sections = []
        
        # If there's text before the first heading, capture it as level 0
        if matches and matches[0].start() > 0:
            intro = md[: matches[0].start()].strip()
            if intro:
                sections.append({"level": 0, "title": None, "content": intro})
        
        # Walk through each heading match and slice out its content
        for idx, m in enumerate(matches):
            level = len(m.group("hashes"))
            title = m.group("title").strip()
            
            start_body = m.end()
            end_body = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
            
            body = md[start_body:end_body].strip()
            sections.append({"level": level, "title": title, "content": body})
        
        # If there were no headings at all, treat the whole doc as one section
        if not matches:
            sections.append({"level": 0, "title": None, "content": md})
        
        return sections

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

