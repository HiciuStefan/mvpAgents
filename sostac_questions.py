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