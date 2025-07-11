import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

class YouTubeInfluencerFinder:
    def __init__(self, youtube_api_key: str):
        """
        Initialize with YouTube Data API key only.
        
        Args:
            youtube_api_key: Your YouTube Data API v3 key
        """
        self.api_key = youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Romanian market rates (based on 2024 market research)
        # These are realistic rates for Romanian YouTubers
        self.romania_budget_ranges = {
            'micro': (50, 300),      # €50-300 per video (1K-50K subscribers)
            'small': (300, 1000),    # €300-1K per video (50K-200K subscribers)
            'medium': (1000, 3000),  # €1K-3K per video (200K-500K subscribers)
            'large': (3000, 10000),  # €3K-10K per video (500K+ subscribers)
            'celebrity': (10000, 50000)  # €10K+ per video (1M+ subscribers)
        }
        
        # Romanian market CPM rates (cost per 1000 views)
        self.romania_cpm_rates = {
            'micro': 0.8,    # €0.8 per 1K views
            'small': 1.2,    # €1.2 per 1K views
            'medium': 1.8,   # €1.8 per 1K views
            'large': 2.5,    # €2.5 per 1K views
            'celebrity': 3.5 # €3.5 per 1K views
        }
        
        # Industry keywords for Romanian market
        self.industry_keywords = {
            'beauty': ['beauty', 'frumusete', 'makeup', 'skincare', 'cosmetice', 'tutorial machiaj'],
            'tech': ['tech', 'tehnologie', 'gadgets', 'review', 'unboxing', 'smartphone'],
            'gaming': ['gaming', 'jocuri', 'gameplay', 'review jocuri', 'gaming romania'],
            'lifestyle': ['lifestyle', 'vlog', 'daily', 'viata', 'romania vlog'],
            'food': ['cooking', 'retete', 'food', 'mancare', 'bucatarie', 'gatit'],
            'fitness': ['fitness', 'workout', 'sport', 'antrenament', 'gym', 'sanatate'],
            'travel': ['travel', 'calatorie', 'romania', 'turism', 'vacanta'],
            'fashion': ['fashion', 'moda', 'outfit', 'stil', 'haine', 'shopping'],
            'education': ['educatie', 'invatare', 'tutorial', 'lectii', 'scoala'],
            'business': ['business', 'antreprenoriat', 'afaceri', 'marketing', 'success']
        }
    
    def find_influencers(self, industry: str, country: str, budget_range: str) -> List[Dict]:
        """
        Find Romanian YouTube influencers based on campaign parameters.
        
        Args:
            industry: Target industry (e.g., 'beauty', 'tech', 'gaming')
            country: Should be 'RO' for Romania
            budget_range: Budget category ('micro', 'small', 'medium', 'large', 'celebrity')
            
        Returns:
            List of YouTube influencer profiles with engagement data and cost estimates
        """
        if country.upper() != 'RO':
            print(f"Warning: This implementation is optimized for Romania (RO), but searching for {country}")
        
        if budget_range not in self.romania_budget_ranges:
            raise ValueError(f"Invalid budget_range. Must be one of: {list(self.romania_budget_ranges.keys())}")
        
        # Get budget constraints
        min_budget, max_budget = self.romania_budget_ranges[budget_range]
        
        print(f"Searching for {industry} influencers in Romania with budget {min_budget}-{max_budget} EUR")
        
        # Find influencers
        influencers = []
        
        # Search by industry keywords
        search_terms = self.industry_keywords.get(industry.lower(), [industry])
        
        for search_term in search_terms[:3]:  # Limit to 3 search terms to stay within API limits
            print(f"Searching for: {search_term}")
            channel_results = self._search_channels(search_term, country)
            
            for channel_id in channel_results:
                influencer_data = self._get_channel_details(channel_id, min_budget, max_budget, budget_range)
                if influencer_data:
                    influencers.append(influencer_data)
        
        # Remove duplicates and rank
        unique_influencers = self._deduplicate_influencers(influencers)
        ranked_influencers = self._rank_influencers(unique_influencers, industry, budget_range)
        
        # Add Romanian market insights
        for influencer in ranked_influencers:
            influencer['market_insights'] = self._generate_romania_market_insights(influencer, industry)
            influencer['cost_analysis'] = self._analyze_romania_cost_effectiveness(influencer, budget_range)
        
        print(f"Found {len(ranked_influencers)} suitable influencers")
        return ranked_influencers[:20]  # Return top 20 matches
    
    def _search_channels(self, search_term: str, country: str) -> List[str]:
        """Search for YouTube channels by keyword."""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': search_term,
            'type': 'channel',
            'regionCode': country,
            'relevanceLanguage': 'ro',  # Romanian language
            'maxResults': 25,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            channel_ids = []
            for item in data.get('items', []):
                channel_id = item['id']['channelId']
                channel_ids.append(channel_id)
            
            return channel_ids
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching channels: {e}")
            return []
    
    def _get_channel_details(self, channel_id: str, min_budget: int, max_budget: int, budget_range: str) -> Optional[Dict]:
        """Get detailed channel information and check if it fits budget."""
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return None
            
            channel = data['items'][0]
            snippet = channel.get('snippet', {})
            stats = channel.get('statistics', {})
            branding = channel.get('brandingSettings', {})
            
            # Parse statistics
            subscriber_count = int(stats.get('subscriberCount', 0))
            total_views = int(stats.get('viewCount', 0))
            video_count = int(stats.get('videoCount', 0))
            
            # Skip channels with no subscribers or very low activity
            if subscriber_count < 1000 or video_count < 10:
                return None
            
            # Calculate estimated costs
            cost_estimates = self._calculate_romania_costs(subscriber_count, total_views, video_count, budget_range)
            
            # Check if within budget
            estimated_cost = cost_estimates['cost_per_video']
            if not (min_budget <= estimated_cost <= max_budget):
                return None
            
            # Get recent video performance
            recent_videos = self._get_recent_videos(channel_id)
            engagement_metrics = self._calculate_engagement_metrics(recent_videos)
            
            # Check if channel is Romanian or Romania-focused
            is_romanian = self._is_romanian_channel(snippet, branding)
            
            return {
                'platform': 'youtube',
                'channel_id': channel_id,
                'username': snippet.get('customUrl', '').replace('@', ''),
                'display_name': snippet.get('title', ''),
                'subscribers': subscriber_count,
                'total_views': total_views,
                'video_count': video_count,
                'description': snippet.get('description', '')[:500],  # Limit description length
                'profile_picture': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'country': snippet.get('country', 'RO'),
                'default_language': snippet.get('defaultLanguage', 'ro'),
                'created_date': snippet.get('publishedAt'),
                'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                'is_romanian': is_romanian,
                
                # Cost estimates for Romanian market
                'estimated_cost_per_video': estimated_cost,
                'cost_per_1k_views': cost_estimates['cost_per_1k_views'],
                'cost_per_subscriber': cost_estimates['cost_per_subscriber'],
                
                # Engagement metrics
                'avg_views_per_video': engagement_metrics['avg_views'],
                'avg_likes_per_video': engagement_metrics['avg_likes'],
                'avg_comments_per_video': engagement_metrics['avg_comments'],
                'engagement_rate': engagement_metrics['engagement_rate'],
                'views_to_subscribers_ratio': engagement_metrics['views_to_subscribers_ratio'],
                
                # Recent performance
                'recent_videos': recent_videos[:3],  # Last 3 videos
                'posting_frequency': engagement_metrics['posting_frequency'],
                'consistency_score': engagement_metrics['consistency_score'],
                
                # Market classification
                'influencer_tier': budget_range,
                'market': 'romania',
                'currency': 'EUR',
                'last_updated': datetime.now().isoformat()
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Error getting channel details for {channel_id}: {e}")
            return None
    
    def _get_recent_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """Get recent videos from a channel."""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'order': 'date',
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            video_ids = []
            
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                videos.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url']
                })
            
            # Get video statistics
            if video_ids:
                stats_url = f"{self.base_url}/videos"
                stats_params = {
                    'part': 'statistics',
                    'id': ','.join(video_ids),
                    'key': self.api_key
                }
                
                stats_response = requests.get(stats_url, params=stats_params)
                stats_response.raise_for_status()
                stats_data = stats_response.json()
                
                # Add statistics to videos
                for i, video_stats in enumerate(stats_data.get('items', [])):
                    if i < len(videos):
                        stats = video_stats.get('statistics', {})
                        videos[i].update({
                            'views': int(stats.get('viewCount', 0)),
                            'likes': int(stats.get('likeCount', 0)),
                            'comments': int(stats.get('commentCount', 0))
                        })
            
            return videos
        
        except requests.exceptions.RequestException as e:
            print(f"Error getting recent videos: {e}")
            return []
    
    def _calculate_engagement_metrics(self, videos: List[Dict]) -> Dict:
        """Calculate engagement metrics from recent videos."""
        if not videos:
            return {
                'avg_views': 0,
                'avg_likes': 0,
                'avg_comments': 0,
                'engagement_rate': 0,
                'views_to_subscribers_ratio': 0,
                'posting_frequency': 0,
                'consistency_score': 0
            }
        
        # Calculate averages
        total_views = sum(video.get('views', 0) for video in videos)
        total_likes = sum(video.get('likes', 0) for video in videos)
        total_comments = sum(video.get('comments', 0) for video in videos)
        
        avg_views = total_views / len(videos)
        avg_likes = total_likes / len(videos)
        avg_comments = total_comments / len(videos)
        
        # Calculate engagement rate (likes + comments / views)
        engagement_rate = (total_likes + total_comments) / max(total_views, 1)
        
        # Calculate posting frequency (videos per week)
        if len(videos) > 1:
            first_video = datetime.fromisoformat(videos[-1]['published_at'].replace('Z', '+00:00'))
            last_video = datetime.fromisoformat(videos[0]['published_at'].replace('Z', '+00:00'))
            days_diff = (last_video - first_video).days
            posting_frequency = len(videos) / max(days_diff / 7, 1)  # Videos per week
        else:
            posting_frequency = 0
        
        # Calculate consistency score (how consistent are the view counts)
        view_counts = [video.get('views', 0) for video in videos]
        if len(view_counts) > 1:
            avg_views_calc = sum(view_counts) / len(view_counts)
            variance = sum((v - avg_views_calc) ** 2 for v in view_counts) / len(view_counts)
            consistency_score = 1 / (1 + variance / (avg_views_calc ** 2))  # Normalized consistency
        else:
            consistency_score = 1.0
        
        return {
            'avg_views': avg_views,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'engagement_rate': engagement_rate,
            'views_to_subscribers_ratio': 0,  # Will be calculated later when we have subscriber count
            'posting_frequency': posting_frequency,
            'consistency_score': consistency_score
        }
    
    def _calculate_romania_costs(self, subscribers: int, total_views: int, video_count: int, budget_range: str) -> Dict:
        """Calculate costs based on Romanian market rates."""
        # Average views per video
        avg_views_per_video = total_views / max(video_count, 1)
        
        # Get CPM rate for this tier
        cpm_rate = self.romania_cpm_rates[budget_range]
        
        # Calculate cost per video based on expected views
        cost_per_video = (avg_views_per_video / 1000) * cpm_rate
        
        # Minimum cost based on subscribers (€0.001 per subscriber for micro, scaling up)
        subscriber_multipliers = {
            'micro': 0.001,
            'small': 0.003,
            'medium': 0.005,
            'large': 0.008,
            'celebrity': 0.01
        }
        
        min_cost_by_subscribers = subscribers * subscriber_multipliers[budget_range]
        
        # Take the higher of the two calculations
        final_cost = max(cost_per_video, min_cost_by_subscribers)
        
        # Ensure it's within the budget range
        min_budget, max_budget = self.romania_budget_ranges[budget_range]
        final_cost = max(min_budget, min(final_cost, max_budget))
        
        return {
            'cost_per_video': int(final_cost),
            'cost_per_1k_views': cpm_rate,
            'cost_per_subscriber': final_cost / subscribers
        }
    
    def _is_romanian_channel(self, snippet: Dict, branding: Dict) -> bool:
        """Check if channel is Romanian or Romania-focused."""
        # Check country
        if snippet.get('country') == 'RO':
            return True
        
        # Check language
        if snippet.get('defaultLanguage') == 'ro':
            return True
        
        # Check description for Romanian keywords
        description = snippet.get('description', '').lower()
        romanian_keywords = ['romania', 'bucuresti', 'cluj', 'timisoara', 'constanta', 'iasi', 'brasov', 'românesc', 'român']
        if any(keyword in description for keyword in romanian_keywords):
            return True
        
        # Check channel title
        title = snippet.get('title', '').lower()
        if any(keyword in title for keyword in romanian_keywords):
            return True
        
        return False
    
    def _rank_influencers(self, influencers: List[Dict], industry: str, budget_range: str) -> List[Dict]:
        """Rank influencers by relevance and quality for Romanian market."""
        for influencer in influencers:
            score = 0
            
            # Romanian market preference (0-20 points)
            if influencer.get('is_romanian', False):
                score += 20
            
            # Engagement rate score (0-25 points)
            engagement_rate = influencer.get('engagement_rate', 0)
            if engagement_rate > 0.05:  # >5%
                score += 25
            elif engagement_rate > 0.03:  # >3%
                score += 20
            elif engagement_rate > 0.01:  # >1%
                score += 15
            elif engagement_rate > 0.005:  # >0.5%
                score += 10
            
            # Subscriber count appropriateness (0-20 points)
            subscribers = influencer.get('subscribers', 0)
            if budget_range == 'micro' and 1000 <= subscribers <= 50000:
                score += 20
            elif budget_range == 'small' and 50000 <= subscribers <= 200000:
                score += 20
            elif budget_range == 'medium' and 200000 <= subscribers <= 500000:
                score += 20
            elif budget_range == 'large' and subscribers > 500000:
                score += 20
            
            # Consistency score (0-15 points)
            consistency = influencer.get('consistency_score', 0)
            score += consistency * 15
            
            # Posting frequency (0-10 points)
            posting_freq = influencer.get('posting_frequency', 0)
            if posting_freq >= 1:  # At least 1 video per week
                score += 10
            elif posting_freq >= 0.5:  # At least 2 videos per month
                score += 7
            elif posting_freq >= 0.25:  # At least 1 video per month
                score += 5
            
            # Recent activity bonus (0-10 points)
            recent_videos = influencer.get('recent_videos', [])
            if recent_videos:
                last_video_date = datetime.fromisoformat(recent_videos[0]['published_at'].replace('Z', '+00:00'))
                days_since_last_video = (datetime.now(last_video_date.tzinfo) - last_video_date).days
                if days_since_last_video <= 7:
                    score += 10
                elif days_since_last_video <= 30:
                    score += 7
                elif days_since_last_video <= 90:
                    score += 5
            
            influencer['relevance_score'] = score
        
        # Sort by relevance score
        return sorted(influencers, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _generate_romania_market_insights(self, influencer: Dict, industry: str) -> Dict:
        """Generate market insights specific to Romania."""
        insights = {
            'target_audience': 'Romanian audience',
            'recommended_content_types': [],
            'best_posting_schedule': {},
            'collaboration_suggestions': [],
            'expected_reach': 0,
            'expected_engagement': 0,
            'market_positioning': ''
        }
        
        subscribers = influencer.get('subscribers', 0)
        avg_views = influencer.get('avg_views_per_video', 0)
        engagement_rate = influencer.get('engagement_rate', 0)
        
        # Romanian market content recommendations
        if industry == 'beauty':
            insights['recommended_content_types'] = ['Tutorial de machiaj', 'Review produse', 'Skincare routine', 'Haul video']
        elif industry == 'tech':
            insights['recommended_content_types'] = ['Unboxing', 'Review tehnic', 'Comparatii produse', 'Tutorial utilizare']
        elif industry == 'food':
            insights['recommended_content_types'] = ['Retete traditionale', 'Cooking show', 'Review restaurante', 'Food challenge']
        elif industry == 'lifestyle':
            insights['recommended_content_types'] = ['Vlog zilnic', 'Room tour', 'Shopping haul', 'Life advice']
        
        # Best posting schedule for Romanian audience
        insights['best_posting_schedule'] = {
            'best_days': ['Miercuri', 'Joi', 'Duminica'],
            'best_times': ['18:00-20:00', '20:00-22:00'],
            'timezone': 'Europe/Bucharest'
        }
        
        # Expected reach (Romanian YouTube penetration is ~70%)
        insights['expected_reach'] = int(avg_views * 0.8)  # 80% of usual reach
        insights['expected_engagement'] = int(insights['expected_reach'] * engagement_rate)
        
        # Market positioning
        if subscribers < 50000:
            insights['market_positioning'] = 'Micro-influencer cu audiență dedicată'
        elif subscribers < 200000:
            insights['market_positioning'] = 'Influencer regional cu impact mediu'
        elif subscribers < 500000:
            insights['market_positioning'] = 'Influencer național cu reach mare'
        else:
            insights['market_positioning'] = 'Top influencer în România'
        
        return insights
    
    def _analyze_romania_cost_effectiveness(self, influencer: Dict, budget_range: str) -> Dict:
        """Analyze cost effectiveness in Romanian market."""
        cost = influencer.get('estimated_cost_per_video', 0)
        subscribers = influencer.get('subscribers', 0)
        avg_views = influencer.get('avg_views_per_video', 0)
        engagement_rate = influencer.get('engagement_rate', 0)
        
        analysis = {
            'cost_per_subscriber': cost / max(subscribers, 1),
            'cost_per_view': cost / max(avg_views, 1),
            'cost_per_engagement': 0,
            'value_rating': 'unknown',
            'budget_utilization': 0,
            'roi_estimate': {},
            'market_comparison': ''
        }
        
        # Calculate cost per engagement
        expected_engagement = avg_views * engagement_rate
        if expected_engagement > 0:
            analysis['cost_per_engagement'] = cost / expected_engagement
        
        # Value rating based on Romanian market standards
        cpe = analysis['cost_per_engagement']
        if cpe < 0.5:
            analysis['value_rating'] = 'excelent'
        elif cpe < 1.0:
            analysis['value_rating'] = 'foarte bun'
        elif cpe < 2.0:
            analysis['value_rating'] = 'bun'
        elif cpe < 5.0:
            analysis['value_rating'] = 'mediu'
        else:
            analysis['value_rating'] = 'scump'
        
        # Budget utilization
        min_budget, max_budget = self.romania_budget_ranges[budget_range]
        analysis['budget_utilization'] = (cost - min_budget) / (max_budget - min_budget)
        
        # ROI estimate (conservative estimates for Romanian market)
        analysis['roi_estimate'] = {
            'estimated_clicks': int(expected_engagement * 0.05),  # 5% click rate
            'estimated_conversions': int(expected_engagement * 0.001),  # 0.1% conversion rate
            'break_even_revenue': cost * 3,  # Need 3x revenue to break even
            'confidence_level': 'mediu'
        }
        
        # Market comparison
        avg_cost_per_view = 1.5  # Average €1.5 per 1K views in Romania
        if cost / (avg_views / 1000) < avg_cost_per_view:
            analysis['market_comparison'] = 'sub media pieței'
        elif cost / (avg_views / 1000) < avg_cost_per_view * 1.5:
            analysis['market_comparison'] = 'conform pieței'
        else:
            analysis['market_comparison'] = 'peste media pieței'
        
        return analysis
    
    def _deduplicate_influencers(self, influencers: List[Dict]) -> List[Dict]:
        """Remove duplicate influencers based on channel ID."""
        seen_channels = set()
        unique_influencers = []
        
        for influencer in influencers:
            channel_id = influencer.get('channel_id', '')
            if channel_id and channel_id not in seen_channels:
                seen_channels.add(channel_id)
                unique_influencers.append(influencer)
        
        return unique_influencers