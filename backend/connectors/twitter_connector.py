"""
Twitter/X Connector

This connector fetches tweets using:
1. Twitter API v2 (primary) - requires TWITTER_BEARER_TOKEN
2. Nitter instances (fallback) - no auth required, experimental

Free Tier Limits (Twitter API v2):
- 1,500 tweets/month for reading
- 1 request/second rate limit
- Only recent tweets (last 7 days)

Environment Variables:
- TWITTER_BEARER_TOKEN: Required for API access
- TWITTER_API_KEY: Optional, for elevated access
- TWITTER_API_SECRET: Optional, for elevated access
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

# Import base classes
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

# Tweepy is optional - we'll handle import error gracefully
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    tweepy = None

# For Nitter fallback
try:
    import requests
    from bs4 import BeautifulSoup
    NITTER_AVAILABLE = True
except ImportError:
    NITTER_AVAILABLE = False


class TwitterConnector(BaseConnector):
    """
    Connector for Twitter/X data.
    
    Usage:
        connector = TwitterConnector()
        
        # Check if configured
        if connector.is_configured():
            result = await connector.fetch("marketing trends")
        
        # Or use with automatic fallback
        result = await connector.fetch_with_fallback("marketing trends")
    """
    
    # Nitter instances to try (some may be down)
    NITTER_INSTANCES = [
        "nitter.net",
        "nitter.it", 
        "nitter.nl",
        "nitter.1d4.us",
        "nitter.kavin.rocks",
    ]
    
    @property
    def name(self) -> str:
        return "twitter"
    
    @property
    def display_name(self) -> str:
        return "Twitter/X"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Twitter connector.
        
        Reads credentials from environment variables:
        - TWITTER_BEARER_TOKEN (required)
        - TWITTER_API_KEY (optional)
        - TWITTER_API_SECRET (optional)
        """
        super().__init__(config)
        
        # Get credentials from env or config
        self.bearer_token = (
            self.config.get("bearer_token") or 
            os.getenv("TWITTER_BEARER_TOKEN")
        )
        self.api_key = (
            self.config.get("api_key") or 
            os.getenv("TWITTER_API_KEY")
        )
        self.api_secret = (
            self.config.get("api_secret") or 
            os.getenv("TWITTER_API_SECRET")
        )
        
        # Initialize tweepy client if available and configured
        self.client = None
        if TWEEPY_AVAILABLE and self.bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    wait_on_rate_limit=False  # Don't wait - return mock data instead
                )
                self.logger.info("Twitter API client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Twitter client: {e}")
    
    def is_configured(self) -> bool:
        """
        Check if Twitter API credentials are available.
        
        Returns True if:
        - tweepy library is installed AND
        - TWITTER_BEARER_TOKEN is set
        """
        if not TWEEPY_AVAILABLE:
            self.logger.warning("tweepy not installed. Run: pip install tweepy")
            return False
        return bool(self.bearer_token)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch tweets from Twitter API.
        
        Args:
            query: Search query (e.g., "marketing trends")
            limit: Max tweets to return (default: 50, max: 100)
            
        Returns:
            ConnectorResult with tweet data
        """
        limit = min(kwargs.get("limit", 50), 100)  # Twitter max is 100
        
        try:
            # Twitter API v2 search
            # Note: Free tier only searches last 7 days
            response = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=["created_at", "public_metrics", "author_id", "lang"],
                expansions=["author_id"],
                user_fields=["username", "name"]
            )
            
            # Handle empty results
            if not response.data:
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=[],
                    source=self.name,
                    message="No tweets found for this query",
                    items_count=0
                )
            
            # Build user lookup dict (author_id -> user info)
            users = {}
            if response.includes and "users" in response.includes:
                for user in response.includes["users"]:
                    users[user.id] = {
                        "username": user.username,
                        "name": user.name
                    }
            
            # Process tweets
            data = []
            for tweet in response.data:
                user_info = users.get(tweet.author_id, {})
                metrics = tweet.public_metrics or {}
                
                data.append({
                    "id": str(tweet.id),
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "author_id": str(tweet.author_id),
                    "author_username": user_info.get("username", "unknown"),
                    "author_name": user_info.get("name", "Unknown"),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                    "language": getattr(tweet, "lang", None),
                    "url": f"https://twitter.com/i/status/{tweet.id}",
                    "source": "twitter_api"
                })
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} tweets from Twitter API",
                items_count=len(data)
            )
            
        except tweepy.TooManyRequests as e:
            self.logger.warning(f"Twitter rate limit hit: {e}")
            # Return mock data with RATE_LIMITED status instead of waiting
            mock_data = self.get_mock_data(query, limit=limit)
            return ConnectorResult(
                status=ConnectorStatus.RATE_LIMITED,
                data=mock_data,
                source=self.name,
                message="Twitter rate limit exceeded - using sample data. Try again later.",
                items_count=len(mock_data),
                error_detail=str(e)
            )
            
        except tweepy.Unauthorized as e:
            self.logger.error(f"Twitter auth failed: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query, limit=limit),
                source=self.name,
                message="Twitter authentication failed - check TWITTER_BEARER_TOKEN",
                items_count=0,
                error_detail=str(e)
            )
            
        except tweepy.Forbidden as e:
            self.logger.error(f"Twitter access forbidden: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query, limit=limit),
                source=self.name,
                message="Twitter access forbidden - may need elevated access",
                items_count=0,
                error_detail=str(e)
            )
            
        except Exception as e:
            self.logger.error(f"Twitter API error: {type(e).__name__}: {e}")
            # Try Nitter fallback before giving up
            nitter_result = await self._fetch_nitter(query, limit)
            if nitter_result.status == ConnectorStatus.SUCCESS:
                return nitter_result
            
            # Both failed, return mock
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query, limit=limit),
                source=self.name,
                message=f"Twitter unavailable - using sample data",
                items_count=0,
                error_detail=f"{type(e).__name__}: {str(e)}"
            )
    
    async def _fetch_nitter(self, query: str, limit: int = 20) -> ConnectorResult:
        """
        Fallback: Fetch tweets from Nitter instances.
        
        Nitter is an open-source Twitter frontend that doesn't require auth.
        Note: This is experimental and may break if Nitter instances go down.
        """
        if not NITTER_AVAILABLE:
            self.logger.warning("requests/beautifulsoup4 not installed for Nitter")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message="Nitter fallback unavailable",
                items_count=0
            )
        
        # Try each Nitter instance
        for instance in self.NITTER_INSTANCES:
            try:
                self.logger.info(f"Trying Nitter instance: {instance}")
                
                # Search URL
                url = f"https://{instance}/search?q={query}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")
                tweets = soup.select(".timeline-item")[:limit]
                
                if not tweets:
                    continue
                
                data = []
                for tweet in tweets:
                    try:
                        # Extract tweet data from HTML
                        content = tweet.select_one(".tweet-content")
                        username = tweet.select_one(".username")
                        stats = tweet.select(".icon-container")
                        
                        text = content.get_text(strip=True) if content else ""
                        user = username.get_text(strip=True) if username else "unknown"
                        
                        # Parse stats (replies, retweets, likes)
                        replies = retweets = likes = 0
                        for stat in stats:
                            stat_text = stat.get_text(strip=True)
                            if "comment" in str(stat):
                                replies = self._parse_count(stat_text)
                            elif "retweet" in str(stat):
                                retweets = self._parse_count(stat_text)
                            elif "heart" in str(stat):
                                likes = self._parse_count(stat_text)
                        
                        data.append({
                            "id": f"nitter_{len(data)}",
                            "text": text,
                            "created_at": None,  # Nitter doesn't always show dates
                            "author_username": user.replace("@", ""),
                            "author_name": user,
                            "likes": likes,
                            "retweets": retweets,
                            "replies": replies,
                            "source": f"nitter_{instance}"
                        })
                    except Exception as e:
                        self.logger.debug(f"Failed to parse tweet: {e}")
                        continue
                
                if data:
                    return ConnectorResult(
                        status=ConnectorStatus.SUCCESS,
                        data=data,
                        source=self.name,
                        message=f"Retrieved {len(data)} tweets via Nitter ({instance})",
                        items_count=len(data)
                    )
                    
            except requests.Timeout:
                self.logger.debug(f"Nitter instance {instance} timed out")
            except Exception as e:
                self.logger.debug(f"Nitter instance {instance} failed: {e}")
        
        # All instances failed
        return ConnectorResult(
            status=ConnectorStatus.FAILED,
            data=[],
            source=self.name,
            message="All Nitter instances unavailable",
            items_count=0
        )
    
    def _parse_count(self, text: str) -> int:
        """Parse count strings like '1.2K' or '5M' to integers"""
        try:
            text = text.strip().upper()
            if not text or text == "":
                return 0
            if "K" in text:
                return int(float(text.replace("K", "")) * 1000)
            if "M" in text:
                return int(float(text.replace("M", "")) * 1000000)
            return int(text)
        except:
            return 0
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return mock tweet data for testing/fallback.
        
        This imports from the existing mock connector to maintain consistency.
        """
        limit = kwargs.get("limit", 20)
        
        # Try to use existing mock data
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from api_connectors_mock import MockTwitterConnector
            mock = MockTwitterConnector()
            return mock.search_tweets(query, limit=limit)
        except ImportError:
            pass
        
        # Fallback: Generate simple mock data
        mock_tweets = []
        for i in range(min(limit, 10)):
            mock_tweets.append({
                "id": f"mock_{i}",
                "text": f"Sample tweet about {query} - This is mock data #{i+1}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "author_username": f"user{i}",
                "author_name": f"Sample User {i}",
                "likes": (i + 1) * 10,
                "retweets": (i + 1) * 5,
                "replies": i,
                "source": "mock"
            })
        return mock_tweets


# Register this connector when module is imported
def _register():
    """Register connector with the factory"""
    try:
        from . import register_connector
        register_connector("twitter", TwitterConnector)
    except ImportError:
        pass  # Will be registered manually if needed

_register()
