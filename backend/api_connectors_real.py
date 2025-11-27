"""
Real API Connectors for Demo 5: Trend Research System

This module provides real API integrations for:
- Twitter/X API (via tweepy)
- TikTok API (via TikTokApi)
- Reddit API (via praw)
- Google Trends API (via pytrends)
- Web Search API (via Bing Search API)

Setup:
1. Install dependencies: pip install tweepy TikTokApi praw pytrends requests
2. Configure API keys in .env file
3. See DEMO5_REAL_APIS_GUIDE.md for detailed setup

For demo/testing without API keys, use api_connectors_mock.py
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class RealTwitterAPI:
    """Real Twitter/X API connector using tweepy"""
    
    def __init__(self):
        self.name = "Twitter/X API"
        self.available = False
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Twitter API client"""
        try:
            import tweepy
            
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            if not bearer_token:
                return
            
            self.client = tweepy.Client(bearer_token=bearer_token)
            self.available = True
            
        except ImportError:
            print("⚠️ tweepy not installed. Run: pip install tweepy")
        except Exception as e:
            print(f"⚠️ Twitter API initialization failed: {str(e)}")
    
    def search_tweets(self, query: str, max_results: int = 100) -> Optional[Dict[str, Any]]:
        """
        Search tweets using Twitter API v2
        
        Args:
            query: Search query
            max_results: Maximum tweets (10-100)
            
        Returns:
            Dictionary with tweets and metrics, or None if failed
        """
        if not self.available or not self.client:
            return None
        
        try:
            # Twitter API v2 max is 100 per request
            max_results = min(max_results, 100)
            
            # Search recent tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'location']
            )
            
            if not response.data:
                return None
            
            # Process tweets
            tweets = []
            total_engagement = 0
            sentiments = []
            hashtags = []
            
            for tweet in response.data:
                metrics = tweet.public_metrics
                engagement = (
                    metrics['like_count'] + 
                    metrics['retweet_count'] + 
                    metrics['reply_count']
                )
                total_engagement += engagement
                
                # Simple sentiment (would use proper sentiment analysis in production)
                sentiment = self._simple_sentiment(tweet.text)
                sentiments.append(sentiment)
                
                # Extract hashtags
                words = tweet.text.split()
                hashtags.extend([w for w in words if w.startswith('#')])
                
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author": f"@{tweet.author_id}",
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "engagement": engagement,
                    "likes": metrics['like_count'],
                    "retweets": metrics['retweet_count'],
                    "replies": metrics['reply_count'],
                    "sentiment": sentiment
                })
            
            # Calculate sentiment breakdown
            total = len(sentiments)
            sentiment_breakdown = {
                "positive": round((sentiments.count("positive") / total) * 100, 1) if total > 0 else 0,
                "neutral": round((sentiments.count("neutral") / total) * 100, 1) if total > 0 else 0,
                "negative": round((sentiments.count("negative") / total) * 100, 1) if total > 0 else 0
            }
            
            # Top hashtags
            from collections import Counter
            top_hashtags = [tag for tag, _ in Counter(hashtags).most_common(5)] if hashtags else []
            
            return {
                "platform": "Twitter/X",
                "query": query,
                "total_results": len(tweets),
                "tweets": tweets,
                "metrics": {
                    "total_engagement": total_engagement,
                    "avg_engagement": total_engagement / len(tweets) if tweets else 0,
                    "sentiment_breakdown": sentiment_breakdown,
                    "top_hashtags": top_hashtags,
                    "peak_hours": ["Data not available in basic API"],
                    "geographic_distribution": {"Data": "Not available in basic API"}
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Twitter API search failed: {str(e)}")
            return None
    
    def _simple_sentiment(self, text: str) -> str:
        """Simple sentiment analysis (replace with proper NLP in production)"""
        text_lower = text.lower()
        
        positive_words = ['great', 'good', 'love', 'amazing', 'excellent', 'best', 'awesome', '🔥', '❤️', '💯']
        negative_words = ['bad', 'hate', 'worst', 'terrible', 'awful', 'poor', 'disappointed', '😔', '😡']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"


class RealTikTokAPI:
    """Real TikTok API connector"""
    
    def __init__(self):
        self.name = "TikTok API"
        self.available = False
        self.api = None
        self._initialize()
    
    def _initialize(self):
        """Initialize TikTok API"""
        try:
            from TikTokApi import TikTokApi
            
            # TikTok API requires specific setup
            # This is a placeholder - actual implementation depends on API access
            self.available = False  # Set to True when properly configured
            print("⚠️ TikTok API requires additional setup. See DEMO5_REAL_APIS_GUIDE.md")
            
        except ImportError:
            print("⚠️ TikTokApi not installed. Run: pip install TikTokApi")
        except Exception as e:
            print(f"⚠️ TikTok API initialization failed: {str(e)}")
    
    def search_videos(self, query: str, max_results: int = 50) -> Optional[Dict[str, Any]]:
        """Search TikTok videos (placeholder - requires proper API setup)"""
        if not self.available:
            return None
        
        # Actual implementation would go here
        return None


class RealRedditAPI:
    """Real Reddit API connector using praw"""
    
    def __init__(self):
        self.name = "Reddit API"
        self.available = False
        self.reddit = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Reddit API client"""
        try:
            import praw
            
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT", "TrendResearchBot/1.0")
            
            if not client_id or not client_secret:
                return
            
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            self.available = True
            
        except ImportError:
            print("⚠️ praw not installed. Run: pip install praw")
        except Exception as e:
            print(f"⚠️ Reddit API initialization failed: {str(e)}")
    
    def search_posts(self, query: str, max_results: int = 100) -> Optional[Dict[str, Any]]:
        """
        Search Reddit posts
        
        Args:
            query: Search query
            max_results: Maximum posts to retrieve
            
        Returns:
            Dictionary with posts and metrics, or None if failed
        """
        if not self.available or not self.reddit:
            return None
        
        try:
            # Search across all of Reddit
            posts = []
            total_upvotes = 0
            total_comments = 0
            subreddits = []
            
            for submission in self.reddit.subreddit("all").search(query, limit=max_results):
                total_upvotes += submission.score
                total_comments += submission.num_comments
                subreddits.append(submission.subreddit.display_name)
                
                posts.append({
                    "id": submission.id,
                    "title": submission.title,
                    "subreddit": f"r/{submission.subreddit.display_name}",
                    "author": f"u/{submission.author.name}" if submission.author else "[deleted]",
                    "created_at": datetime.fromtimestamp(submission.created_utc).isoformat(),
                    "upvotes": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "comments": submission.num_comments,
                    "awards": submission.total_awards_received,
                    "text_preview": submission.selftext[:200] if submission.selftext else "[Link post]"
                })
            
            # Top subreddits
            from collections import Counter
            top_subreddits = [f"r/{sub}" for sub, _ in Counter(subreddits).most_common(5)]
            
            return {
                "platform": "Reddit",
                "query": query,
                "total_results": len(posts),
                "posts": posts,
                "metrics": {
                    "total_upvotes": total_upvotes,
                    "avg_upvotes": total_upvotes / len(posts) if posts else 0,
                    "total_comments": total_comments,
                    "top_subreddits": top_subreddits,
                    "discussion_intensity": "High" if len(posts) > 50 else "Medium",
                    "sentiment_trend": "Mixed"  # Would need sentiment analysis
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Reddit API search failed: {str(e)}")
            return None


class RealGoogleTrendsAPI:
    """Real Google Trends API connector using pytrends"""
    
    def __init__(self):
        self.name = "Google Trends API"
        self.available = False
        self.pytrends = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Trends client"""
        try:
            from pytrends.request import TrendReq
            
            self.pytrends = TrendReq(hl='en-US', tz=360)
            self.available = True
            
        except ImportError:
            print("⚠️ pytrends not installed. Run: pip install pytrends")
        except Exception as e:
            print(f"⚠️ Google Trends initialization failed: {str(e)}")
    
    def get_trends(self, query: str, geo: str = "NG") -> Optional[Dict[str, Any]]:
        """
        Get Google Trends data
        
        Args:
            query: Search term
            geo: Geographic region (e.g., "NG" for Nigeria)
            
        Returns:
            Dictionary with trends data, or None if failed
        """
        if not self.available or not self.pytrends:
            return None
        
        try:
            # Build payload
            self.pytrends.build_payload([query], cat=0, timeframe='today 12-m', geo=geo)
            
            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()
            timeline = []
            if not interest_over_time.empty:
                for date, row in interest_over_time.iterrows():
                    timeline.append({
                        "date": date.strftime("%Y-%m"),
                        "value": int(row[query])
                    })
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            related_list = []
            if query in related_queries and related_queries[query]['top'] is not None:
                related_list = related_queries[query]['top']['query'].head(5).tolist()
            
            # Get interest by region
            interest_by_region = self.pytrends.interest_by_region(resolution='REGION')
            regional_interest = {}
            if not interest_by_region.empty:
                top_regions = interest_by_region.nlargest(5, query)
                for region, row in top_regions.iterrows():
                    regional_interest[region] = int(row[query])
            
            # Calculate search volume index (average of last 3 months)
            search_volume_index = 0
            if timeline:
                recent_values = [t['value'] for t in timeline[-3:]]
                search_volume_index = sum(recent_values) // len(recent_values)
            
            # Determine trending status
            trending_status = "Steady"
            if len(timeline) >= 2:
                if timeline[-1]['value'] > timeline[-2]['value'] * 1.2:
                    trending_status = "Rising"
                elif timeline[-1]['value'] < timeline[-2]['value'] * 0.8:
                    trending_status = "Declining"
            
            return {
                "platform": "Google Trends",
                "query": query,
                "geography": geo,
                "interest_over_time": timeline,
                "related_queries": related_list,
                "related_topics": [],  # Would need additional API call
                "regional_interest": regional_interest,
                "trending_status": trending_status,
                "search_volume_index": search_volume_index,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Google Trends API failed: {str(e)}")
            return None


class RealWebSearchAPI:
    """Real Web Search API using Bing Search API"""
    
    def __init__(self):
        self.name = "Web Search API"
        self.available = False
        self.api_key = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Bing Search API"""
        try:
            import requests
            
            self.api_key = os.getenv("BING_SEARCH_API_KEY")
            if not self.api_key:
                return
            
            self.available = True
            
        except ImportError:
            print("⚠️ requests not installed. Run: pip install requests")
        except Exception as e:
            print(f"⚠️ Web Search API initialization failed: {str(e)}")
    
    def search(self, query: str, max_results: int = 20) -> Optional[Dict[str, Any]]:
        """
        Search web using Bing Search API
        
        Args:
            query: Search query
            max_results: Maximum results (up to 50)
            
        Returns:
            Dictionary with search results, or None if failed
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            import requests
            
            endpoint = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {
                "q": query,
                "count": min(max_results, 50),
                "mkt": "en-US"
            }
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "webPages" not in data or "value" not in data["webPages"]:
                return None
            
            # Process results
            results = []
            news_count = 0
            blog_count = 0
            
            for item in data["webPages"]["value"]:
                # Categorize content type
                url_lower = item["url"].lower()
                if any(news in url_lower for news in ['news', 'article', 'press']):
                    content_type = "News"
                    news_count += 1
                elif any(blog in url_lower for blog in ['blog', 'post', 'medium']):
                    content_type = "Blog Post"
                    blog_count += 1
                else:
                    content_type = "Article"
                
                results.append({
                    "id": item.get("id", ""),
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "source": item.get("displayUrl", "").split('/')[0],
                    "published_date": item.get("dateLastCrawled", datetime.now().isoformat()),
                    "snippet": item.get("snippet", ""),
                    "relevance_score": 1.0,  # Bing doesn't provide this directly
                    "content_type": content_type
                })
            
            return {
                "platform": "Web Search",
                "query": query,
                "total_results": len(results),
                "results": results,
                "metrics": {
                    "news_articles": news_count,
                    "blog_posts": blog_count,
                    "academic_papers": 0,  # Would need specific filtering
                    "social_mentions": 0,  # Would need social search
                    "top_domains": list(set([r["source"] for r in results[:5]])),
                    "content_freshness": "Recent"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Web Search API failed: {str(e)}")
            return None


# Factory function to get all real APIs
def get_real_apis() -> Dict[str, Any]:
    """
    Get all real API connectors
    
    Returns:
        Dictionary of API connectors with availability status
    """
    apis = {
        "twitter": RealTwitterAPI(),
        "tiktok": RealTikTokAPI(),
        "reddit": RealRedditAPI(),
        "google_trends": RealGoogleTrendsAPI(),
        "web_search": RealWebSearchAPI()
    }
    
    # Print availability status
    print("\n📊 API Availability Status:")
    for name, api in apis.items():
        status = "✅ Available" if api.available else "❌ Not configured"
        print(f"  {api.name}: {status}")
    print()
    
    return apis


# Test function
if __name__ == "__main__":
    print("Testing Real APIs...")
    print("=" * 50)
    
    apis = get_real_apis()
    test_query = "Gen Z Nigeria Facebook"
    
    print(f"\nTest Query: '{test_query}'")
    print("=" * 50)
    
    # Test each API
    if apis["twitter"].available:
        print(f"\n1. Testing Twitter API...")
        twitter_data = apis["twitter"].search_tweets(test_query, max_results=10)
        if twitter_data:
            print(f"   ✅ Found {twitter_data['total_results']} tweets")
        else:
            print(f"   ❌ No results")
    
    if apis["reddit"].available:
        print(f"\n2. Testing Reddit API...")
        reddit_data = apis["reddit"].search_posts(test_query, max_results=10)
        if reddit_data:
            print(f"   ✅ Found {reddit_data['total_results']} posts")
        else:
            print(f"   ❌ No results")
    
    if apis["google_trends"].available:
        print(f"\n3. Testing Google Trends API...")
        trends_data = apis["google_trends"].get_trends(test_query)
        if trends_data:
            print(f"   ✅ Search volume index: {trends_data['search_volume_index']}")
        else:
            print(f"   ❌ No results")
    
    if apis["web_search"].available:
        print(f"\n4. Testing Web Search API...")
        search_data = apis["web_search"].search(test_query, max_results=10)
        if search_data:
            print(f"   ✅ Found {search_data['total_results']} results")
        else:
            print(f"   ❌ No results")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
