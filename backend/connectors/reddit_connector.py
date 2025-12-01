"""
Reddit Connector

This connector fetches posts and comments from Reddit using PRAW.

Free Tier Limits:
- 60 requests/minute (without OAuth)
- 100 requests/minute (with OAuth)
- No monthly limits for reasonable use

Environment Variables:
- REDDIT_CLIENT_ID: Required - from https://www.reddit.com/prefs/apps
- REDDIT_CLIENT_SECRET: Required - from app settings
- REDDIT_USER_AGENT: Optional - defaults to "TrendResearchBot/1.0"

PRAW (Python Reddit API Wrapper):
- Official library maintained by Reddit
- Handles rate limiting automatically
- Supports search, hot posts, new posts, etc.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

# PRAW is optional
try:
    import praw
    from praw.exceptions import RedditAPIException
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    praw = None


class RedditConnector(BaseConnector):
    """
    Connector for Reddit data using PRAW.
    
    Features:
    - Search posts by keyword
    - Filter by subreddit
    - Get post comments
    - Sort by relevance, hot, new, top
    
    Usage:
        connector = RedditConnector()
        
        # Search all of Reddit
        result = await connector.fetch("marketing trends")
        
        # Search specific subreddit
        result = await connector.fetch("marketing trends", subreddit="marketing")
        
        # Get hot posts from a subreddit
        result = await connector.fetch_hot("marketing", limit=25)
    """
    
    @property
    def name(self) -> str:
        return "reddit"
    
    @property
    def display_name(self) -> str:
        return "Reddit"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Reddit connector.
        
        PRAW uses "read-only" mode with client credentials.
        This is perfect for search/read operations.
        """
        super().__init__(config)
        
        # Get credentials
        self.client_id = (
            self.config.get("client_id") or 
            os.getenv("REDDIT_CLIENT_ID")
        )
        self.client_secret = (
            self.config.get("client_secret") or 
            os.getenv("REDDIT_CLIENT_SECRET")
        )
        self.user_agent = (
            self.config.get("user_agent") or 
            os.getenv("REDDIT_USER_AGENT", "TrendResearchBot/1.0 (research project)")
        )
        
        # Initialize PRAW client
        self.reddit = None
        if PRAW_AVAILABLE and self.is_configured():
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                # Test the connection (read-only mode)
                self.reddit.read_only = True
                self.logger.info("Reddit PRAW client initialized (read-only)")
            except Exception as e:
                self.logger.error(f"Failed to initialize Reddit client: {e}")
    
    def is_configured(self) -> bool:
        """
        Check if Reddit API credentials are available.
        
        Requires both client_id and client_secret.
        """
        if not PRAW_AVAILABLE:
            self.logger.warning("praw not installed. Run: pip install praw")
            return False
        return bool(self.client_id and self.client_secret)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Search Reddit for posts matching query.
        
        Args:
            query: Search query string
            subreddit: Subreddit to search (default: "all" for all of Reddit)
            limit: Max posts to return (default: 50)
            sort: Sort order - "relevance", "hot", "top", "new" (default: "relevance")
            time_filter: Time range - "hour", "day", "week", "month", "year", "all"
            include_comments: Whether to fetch top comments (slower, default: False)
            
        Returns:
            ConnectorResult with post data
        """
        subreddit = kwargs.get("subreddit", "all")
        limit = min(kwargs.get("limit", 50), 100)  # Reddit max is usually 100
        sort = kwargs.get("sort", "relevance")
        time_filter = kwargs.get("time_filter", "month")
        include_comments = kwargs.get("include_comments", False)
        
        try:
            # Run PRAW in thread pool (it's synchronous)
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._search_sync(query, subreddit, limit, sort, time_filter, include_comments)
            )
            
            if not data:
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=[],
                    source=self.name,
                    message=f"No posts found for '{query}' in r/{subreddit}",
                    items_count=0
                )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} posts from r/{subreddit}",
                items_count=len(data)
            )
            
        except Exception as e:
            error_type = type(e).__name__
            self.logger.error(f"Reddit error: {error_type}: {e}")
            
            # Check for specific errors
            if "401" in str(e) or "unauthorized" in str(e).lower():
                return ConnectorResult(
                    status=ConnectorStatus.FAILED,
                    data=self.get_mock_data(query, limit=limit),
                    source=self.name,
                    message="Reddit authentication failed - check CLIENT_ID and CLIENT_SECRET",
                    items_count=0,
                    error_detail=str(e)
                )
            
            if "429" in str(e) or "rate" in str(e).lower():
                return ConnectorResult(
                    status=ConnectorStatus.RATE_LIMITED,
                    data=self.get_mock_data(query, limit=limit),
                    source=self.name,
                    message="Reddit rate limit hit - try again in a minute",
                    items_count=0,
                    error_detail=str(e)
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query, limit=limit),
                source=self.name,
                message="Reddit unavailable - using sample data",
                items_count=0,
                error_detail=f"{error_type}: {str(e)}"
            )
    
    def _search_sync(
        self, 
        query: str, 
        subreddit: str, 
        limit: int, 
        sort: str,
        time_filter: str,
        include_comments: bool
    ) -> List[Dict[str, Any]]:
        """
        Synchronous search (PRAW is not async-native).
        
        This runs in a thread pool via asyncio.run_in_executor.
        """
        data = []
        
        # Get subreddit object
        sub = self.reddit.subreddit(subreddit)
        
        # Search posts
        for post in sub.search(query, sort=sort, time_filter=time_filter, limit=limit):
            post_data = {
                "id": post.id,
                "title": post.title,
                "text": post.selftext[:1000] if post.selftext else "",  # Limit text length
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "subreddit": str(post.subreddit),
                "subreddit_subscribers": post.subreddit.subscribers if hasattr(post.subreddit, 'subscribers') else None,
                "author": str(post.author) if post.author else "[deleted]",
                "created_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                "url": f"https://reddit.com{post.permalink}",
                "is_self": post.is_self,  # True if text post, False if link
                "link_url": post.url if not post.is_self else None,
                "awards": post.total_awards_received,
                "type": "post"
            }
            
            # Optionally fetch top comments
            if include_comments and post.num_comments > 0:
                post_data["top_comments"] = self._get_top_comments(post, limit=3)
            
            data.append(post_data)
        
        return data
    
    def _get_top_comments(self, post, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get top comments from a post.
        
        Note: This makes additional API calls, so use sparingly.
        """
        comments = []
        try:
            post.comments.replace_more(limit=0)  # Don't load "more comments"
            for comment in post.comments[:limit]:
                if hasattr(comment, 'body'):
                    comments.append({
                        "id": comment.id,
                        "body": comment.body[:500],
                        "score": comment.score,
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "created_utc": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat()
                    })
        except Exception as e:
            self.logger.debug(f"Failed to get comments: {e}")
        
        return comments
    
    async def fetch_hot(self, subreddit: str, limit: int = 25) -> ConnectorResult:
        """
        Fetch hot posts from a subreddit (not search-based).
        
        Args:
            subreddit: Subreddit name (without r/)
            limit: Number of posts
            
        Returns:
            ConnectorResult with hot posts
        """
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._fetch_hot_sync(subreddit, limit)
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} hot posts from r/{subreddit}",
                items_count=len(data)
            )
        except Exception as e:
            self.logger.error(f"Reddit hot posts error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=f"Failed to fetch hot posts from r/{subreddit}",
                items_count=0,
                error_detail=str(e)
            )
    
    def _fetch_hot_sync(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Synchronous fetch of hot posts"""
        data = []
        sub = self.reddit.subreddit(subreddit)
        
        for post in sub.hot(limit=limit):
            data.append({
                "id": post.id,
                "title": post.title,
                "text": post.selftext[:1000] if post.selftext else "",
                "score": post.score,
                "num_comments": post.num_comments,
                "subreddit": str(post.subreddit),
                "author": str(post.author) if post.author else "[deleted]",
                "created_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                "url": f"https://reddit.com{post.permalink}",
                "type": "post"
            })
        
        return data
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return mock Reddit data for testing/fallback.
        """
        limit = kwargs.get("limit", 20)
        
        # Try existing mock connector
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from api_connectors_mock import MockRedditConnector
            mock = MockRedditConnector()
            return mock.search_posts(query, limit=limit)
        except ImportError:
            pass
        
        # Fallback mock data
        mock_posts = []
        subreddits = ["marketing", "socialmedia", "digital_marketing", "business"]
        
        for i in range(min(limit, 10)):
            mock_posts.append({
                "id": f"mock_{i}",
                "title": f"Discussion about {query} - Sample post #{i+1}",
                "text": f"This is sample text about {query}. Many people are interested in this topic.",
                "score": (i + 1) * 100,
                "num_comments": (i + 1) * 10,
                "subreddit": subreddits[i % len(subreddits)],
                "author": f"sample_user_{i}",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "url": f"https://reddit.com/r/marketing/comments/mock{i}",
                "type": "post",
                "source": "mock"
            })
        
        return mock_posts


# Register connector
def _register():
    try:
        from . import register_connector
        register_connector("reddit", RedditConnector)
    except ImportError:
        pass

_register()
