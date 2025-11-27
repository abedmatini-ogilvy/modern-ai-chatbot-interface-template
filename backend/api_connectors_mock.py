"""
Mock API Connectors for Demo 5: Trend Research System

This module provides realistic mock data for:
- Twitter/X API
- TikTok API
- Reddit API
- Google Trends API
- Web Search API

For production use, see api_connectors_real.py
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class MockTwitterAPI:
    """Mock Twitter/X API connector with realistic data"""
    
    def __init__(self):
        self.name = "Twitter/X API"
        
    def search_tweets(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Mock Twitter search with realistic responses
        
        Args:
            query: Search query
            max_results: Maximum number of tweets to return
            
        Returns:
            Dictionary with tweets, metrics, and sentiment
        """
        time.sleep(random.uniform(1.5, 2.5))  # Simulate API delay
        
        # Sample tweets based on query keywords
        tweets = self._generate_tweets(query, max_results)
        
        return {
            "platform": "Twitter/X",
            "query": query,
            "total_results": len(tweets),
            "tweets": tweets,
            "metrics": {
                "total_engagement": sum(t["engagement"] for t in tweets),
                "avg_engagement": sum(t["engagement"] for t in tweets) / len(tweets),
                "sentiment_breakdown": self._calculate_sentiment(tweets),
                "top_hashtags": self._extract_hashtags(tweets),
                "peak_hours": ["9AM-11AM", "6PM-9PM"],
                "geographic_distribution": {
                    "Nigeria": 45,
                    "Ghana": 25,
                    "Kenya": 15,
                    "South Africa": 10,
                    "Other": 5
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_tweets(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic tweet data based on query"""
        
        # Query-specific tweet templates
        templates = {
            "gen z nigeria facebook": [
                "Facebook groups in Nigeria are where the real community vibes are 🇳🇬 #GenZ",
                "Why do we use Facebook for everything except what it was made for? 😂 #NigerianGenZ",
                "Google is for homework, Facebook is for life updates. That's the rule. #Nigeria",
                "Facebook marketplace > Google shopping in Nigeria. Change my mind 💯",
                "The way Nigerian Gen Z has repurposed Facebook is actually genius 🧠"
            ],
            "detty december": [
                "Detty December 2024 was insane! Already planning for next year 🎉 #DettyDecember",
                "The diaspora energy during Detty December hits different 🔥 #Ghana #Nigeria",
                "Spent my entire savings on Detty December. Worth it? Absolutely 💸 #Lagos",
                "Detty December is not just parties, it's reconnecting with home ❤️ #Diaspora",
                "Hotels are already booked for next Detty December 😅 #AccraToLagos"
            ],
            "african creators": [
                "Being a creator in Africa is tough but we're making it work 💪 #AfricanCreators",
                "Payment platforms need to support African creators better! #CreatorEconomy",
                "The talent is here, the infrastructure isn't 😔 #AfricanGamers",
                "Shoutout to all African creators grinding despite the challenges 🙌",
                "We need more monetization options for African content creators #Support"
            ],
            "mpesa": [
                "M-Pesa changed the game for East Africa 🚀 #MobileMoney",
                "Why is M-Pesa so dominant? Because it just works 💯 #Kenya",
                "Every competitor tries but M-Pesa stays winning #EastAfrica",
                "M-Pesa fees are high but convenience is unmatched 🤷‍♂️",
                "The trust factor with M-Pesa is real #DigitalPayments"
            ]
        }
        
        # Select appropriate templates
        query_lower = query.lower()
        selected_templates = []
        for key, tweets in templates.items():
            if any(word in query_lower for word in key.split()):
                selected_templates.extend(tweets)
        
        if not selected_templates:
            selected_templates = [
                f"Interesting insights about {query} 🤔",
                f"The {query} conversation is heating up 🔥",
                f"Everyone's talking about {query} lately 💬"
            ]
        
        # Generate tweets
        tweets = []
        for i in range(min(count, len(selected_templates) * 3)):
            template = random.choice(selected_templates)
            tweets.append({
                "id": f"tweet_{i+1}",
                "text": template,
                "author": f"@user{random.randint(1000, 9999)}",
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "engagement": random.randint(50, 5000),
                "likes": random.randint(20, 2000),
                "retweets": random.randint(5, 500),
                "replies": random.randint(2, 200),
                "sentiment": random.choice(["positive", "positive", "neutral", "negative"])
            })
        
        return tweets[:count]
    
    def _calculate_sentiment(self, tweets: List[Dict]) -> Dict[str, float]:
        """Calculate sentiment distribution"""
        sentiments = [t["sentiment"] for t in tweets]
        total = len(sentiments)
        return {
            "positive": round((sentiments.count("positive") / total) * 100, 1),
            "neutral": round((sentiments.count("neutral") / total) * 100, 1),
            "negative": round((sentiments.count("negative") / total) * 100, 1)
        }
    
    def _extract_hashtags(self, tweets: List[Dict]) -> List[str]:
        """Extract top hashtags from tweets"""
        hashtags = []
        for tweet in tweets:
            words = tweet["text"].split()
            hashtags.extend([w for w in words if w.startswith("#")])
        
        # Count and return top 5
        from collections import Counter
        if hashtags:
            return [tag for tag, _ in Counter(hashtags).most_common(5)]
        return ["#Trending", "#Africa", "#Tech", "#Culture", "#Business"]


class MockTikTokAPI:
    """Mock TikTok API connector with realistic data"""
    
    def __init__(self):
        self.name = "TikTok API"
    
    def search_videos(self, query: str, max_results: int = 50) -> Dict[str, Any]:
        """Mock TikTok video search"""
        time.sleep(random.uniform(1.5, 2.5))
        
        videos = self._generate_videos(query, max_results)
        
        return {
            "platform": "TikTok",
            "query": query,
            "total_results": len(videos),
            "videos": videos,
            "metrics": {
                "total_views": sum(v["views"] for v in videos),
                "avg_views": sum(v["views"] for v in videos) / len(videos),
                "total_engagement_rate": round(random.uniform(5.0, 15.0), 2),
                "trending_sounds": self._get_trending_sounds(query),
                "top_creators": [f"@creator{i}" for i in range(1, 6)],
                "age_demographics": {
                    "13-17": 15,
                    "18-24": 45,
                    "25-34": 30,
                    "35+": 10
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic TikTok video data"""
        videos = []
        
        for i in range(count):
            videos.append({
                "id": f"video_{i+1}",
                "description": f"#{query.replace(' ', '')} content that's going viral 🔥",
                "creator": f"@creator{random.randint(100, 999)}",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "views": random.randint(10000, 1000000),
                "likes": random.randint(500, 50000),
                "comments": random.randint(50, 5000),
                "shares": random.randint(20, 2000),
                "engagement_rate": round(random.uniform(3.0, 12.0), 2),
                "duration_seconds": random.randint(15, 60)
            })
        
        return videos
    
    def _get_trending_sounds(self, query: str) -> List[str]:
        """Get trending sounds related to query"""
        sounds = [
            "Original Sound - Trending",
            "Afrobeats Mix 2024",
            "Viral Dance Challenge",
            "Comedy Skit Audio",
            "Motivational Speech"
        ]
        return random.sample(sounds, 3)


class MockRedditAPI:
    """Mock Reddit API connector with realistic data"""
    
    def __init__(self):
        self.name = "Reddit API"
    
    def search_posts(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        """Mock Reddit post search"""
        time.sleep(random.uniform(1.5, 2.5))
        
        posts = self._generate_posts(query, max_results)
        
        return {
            "platform": "Reddit",
            "query": query,
            "total_results": len(posts),
            "posts": posts,
            "metrics": {
                "total_upvotes": sum(p["upvotes"] for p in posts),
                "avg_upvotes": sum(p["upvotes"] for p in posts) / len(posts),
                "total_comments": sum(p["comments"] for p in posts),
                "top_subreddits": self._get_top_subreddits(query),
                "discussion_intensity": "High" if len(posts) > 50 else "Medium",
                "sentiment_trend": "Positive" if random.random() > 0.5 else "Mixed"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_posts(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic Reddit post data"""
        posts = []
        
        subreddits = ["r/Africa", "r/Nigeria", "r/Kenya", "r/Ghana", "r/technology", "r/marketing"]
        
        for i in range(count):
            posts.append({
                "id": f"post_{i+1}",
                "title": f"Discussion: {query} - What are your thoughts?",
                "subreddit": random.choice(subreddits),
                "author": f"u/user{random.randint(1000, 9999)}",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                "upvotes": random.randint(10, 5000),
                "upvote_ratio": round(random.uniform(0.7, 0.98), 2),
                "comments": random.randint(5, 500),
                "awards": random.randint(0, 10),
                "text_preview": f"Interesting perspective on {query}..."
            })
        
        return posts
    
    def _get_top_subreddits(self, query: str) -> List[str]:
        """Get top subreddits for query"""
        return ["r/Africa", "r/Nigeria", "r/technology", "r/marketing", "r/business"]


class MockGoogleTrendsAPI:
    """Mock Google Trends API connector with realistic data"""
    
    def __init__(self):
        self.name = "Google Trends API"
    
    def get_trends(self, query: str, geo: str = "NG") -> Dict[str, Any]:
        """Mock Google Trends data"""
        time.sleep(random.uniform(1.0, 2.0))
        
        return {
            "platform": "Google Trends",
            "query": query,
            "geography": geo,
            "interest_over_time": self._generate_interest_timeline(),
            "related_queries": self._get_related_queries(query),
            "related_topics": self._get_related_topics(query),
            "regional_interest": {
                "Lagos": 100,
                "Abuja": 75,
                "Port Harcourt": 60,
                "Kano": 45,
                "Ibadan": 55
            },
            "trending_status": random.choice(["Rising", "Steady", "Declining"]),
            "search_volume_index": random.randint(40, 100),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_interest_timeline(self) -> List[Dict[str, Any]]:
        """Generate interest over time data"""
        timeline = []
        base_value = random.randint(40, 80)
        
        for i in range(12):  # Last 12 months
            date = datetime.now() - timedelta(days=30 * (11 - i))
            value = base_value + random.randint(-20, 20)
            timeline.append({
                "date": date.strftime("%Y-%m"),
                "value": max(0, min(100, value))
            })
        
        return timeline
    
    def _get_related_queries(self, query: str) -> List[str]:
        """Get related search queries"""
        related = [
            f"{query} 2024",
            f"best {query}",
            f"{query} near me",
            f"how to {query}",
            f"{query} price"
        ]
        return random.sample(related, 3)
    
    def _get_related_topics(self, query: str) -> List[str]:
        """Get related topics"""
        topics = [
            "Technology", "Business", "Culture", "Entertainment", 
            "Finance", "Social Media", "Innovation", "Lifestyle"
        ]
        return random.sample(topics, 4)


class MockWebSearchAPI:
    """Mock Web Search API connector with realistic data"""
    
    def __init__(self):
        self.name = "Web Search API"
    
    def search(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Mock web search results"""
        time.sleep(random.uniform(1.0, 2.0))
        
        results = self._generate_search_results(query, max_results)
        
        return {
            "platform": "Web Search",
            "query": query,
            "total_results": len(results),
            "results": results,
            "metrics": {
                "news_articles": random.randint(5, 15),
                "blog_posts": random.randint(10, 30),
                "academic_papers": random.randint(2, 8),
                "social_mentions": random.randint(50, 200),
                "top_domains": ["techcabal.com", "disrupt-africa.com", "venturesafrica.com"],
                "content_freshness": "Recent" if random.random() > 0.5 else "Mixed"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_search_results(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic search results"""
        results = []
        
        sources = [
            "TechCabal", "Disrupt Africa", "Ventures Africa", "The Guardian Nigeria",
            "Punch Newspapers", "Premium Times", "Nairametrics", "Business Day"
        ]
        
        for i in range(count):
            results.append({
                "id": f"result_{i+1}",
                "title": f"{query}: Latest Insights and Analysis",
                "url": f"https://example.com/article-{i+1}",
                "source": random.choice(sources),
                "published_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "snippet": f"Comprehensive analysis of {query} trends in African markets...",
                "relevance_score": round(random.uniform(0.7, 1.0), 2),
                "content_type": random.choice(["Article", "Blog Post", "News", "Report"])
            })
        
        return results


# Factory function to get all mock APIs
def get_mock_apis() -> Dict[str, Any]:
    """
    Get all mock API connectors
    
    Returns:
        Dictionary of API connectors
    """
    return {
        "twitter": MockTwitterAPI(),
        "tiktok": MockTikTokAPI(),
        "reddit": MockRedditAPI(),
        "google_trends": MockGoogleTrendsAPI(),
        "web_search": MockWebSearchAPI()
    }


# Test function
if __name__ == "__main__":
    print("Testing Mock APIs...")
    
    apis = get_mock_apis()
    test_query = "Gen Z Nigeria Facebook"
    
    print(f"\n1. Testing Twitter API...")
    twitter_data = apis["twitter"].search_tweets(test_query, max_results=10)
    print(f"   Found {twitter_data['total_results']} tweets")
    print(f"   Sentiment: {twitter_data['metrics']['sentiment_breakdown']}")
    
    print(f"\n2. Testing TikTok API...")
    tiktok_data = apis["tiktok"].search_videos(test_query, max_results=10)
    print(f"   Found {tiktok_data['total_results']} videos")
    print(f"   Avg views: {tiktok_data['metrics']['avg_views']:,.0f}")
    
    print(f"\n3. Testing Reddit API...")
    reddit_data = apis["reddit"].search_posts(test_query, max_results=10)
    print(f"   Found {reddit_data['total_results']} posts")
    print(f"   Top subreddits: {reddit_data['metrics']['top_subreddits']}")
    
    print(f"\n4. Testing Google Trends API...")
    trends_data = apis["google_trends"].get_trends(test_query)
    print(f"   Search volume index: {trends_data['search_volume_index']}")
    print(f"   Status: {trends_data['trending_status']}")
    
    print(f"\n5. Testing Web Search API...")
    search_data = apis["web_search"].search(test_query, max_results=10)
    print(f"   Found {search_data['total_results']} results")
    print(f"   Top domains: {search_data['metrics']['top_domains']}")
    
    print("\n✅ All mock APIs working!")
