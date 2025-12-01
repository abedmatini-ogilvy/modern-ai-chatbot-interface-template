"""
TikTok Connector

TikTok API access is limited compared to other platforms.
This connector supports:
1. TikTok Research API (requires business approval)
2. TikTok Creative Center (trends data)
3. Mock data fallback

Why TikTok is Different:
- No public search API like Twitter/Reddit
- Research API requires business account and approval
- Creative Center provides trends but limited data

Environment Variables:
- TIKTOK_CLIENT_KEY: From TikTok Developer Portal
- TIKTOK_CLIENT_SECRET: From TikTok Developer Portal
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TikTokConnector(BaseConnector):
    """
    Connector for TikTok data.
    
    NOTE: TikTok has very limited API access compared to other platforms.
    
    Options:
    1. Research API (requires approval)
    2. Creative Center API (limited to trends)
    3. Mock data (default fallback)
    
    For MVP, this connector will primarily use mock data unless
    you have TikTok Research API access.
    
    Usage:
        connector = TikTokConnector()
        
        # Will use real API if configured, else mock data
        result = await connector.fetch("marketing trends")
    """
    
    @property
    def name(self) -> str:
        return "tiktok"
    
    @property
    def display_name(self) -> str:
        return "TikTok"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize TikTok connector.
        
        API access is limited - will use mock data in most cases.
        """
        super().__init__(config)
        
        # TikTok API credentials (if available)
        self.client_key = (
            self.config.get("client_key") or
            os.getenv("TIKTOK_CLIENT_KEY")
        )
        self.client_secret = (
            self.config.get("client_secret") or
            os.getenv("TIKTOK_CLIENT_SECRET")
        )
        
        # Access token (obtained via OAuth)
        self._access_token = None
        
        # Log configuration status
        if self.is_configured():
            self.logger.info("TikTok API credentials found")
        else:
            self.logger.info("TikTok using mock data (API not configured)")
    
    def is_configured(self) -> bool:
        """
        Check if TikTok API is configured.
        
        NOTE: Even with credentials, you need approved API access.
        """
        return bool(self.client_key and self.client_secret)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch TikTok data.
        
        Args:
            query: Search query
            limit: Max results (default: 20)
            
        Returns:
            ConnectorResult with TikTok data
            
        Note: Due to API limitations, this often returns mock data.
        """
        limit = kwargs.get("limit", 20)
        
        # If not configured, return mock data immediately
        if not self.is_configured():
            mock_data = self.get_mock_data(query, limit=limit)
            return ConnectorResult(
                status=ConnectorStatus.NOT_CONFIGURED,
                data=mock_data,
                source=self.name,
                message="TikTok API not configured - using sample data",
                items_count=len(mock_data)
            )
        
        # Try to use real API
        try:
            # First, get access token if needed
            if not self._access_token:
                await self._get_access_token()
            
            # Try Research API search
            data = await self._search_videos(query, limit)
            
            if data:
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=data,
                    source=self.name,
                    message=f"Retrieved {len(data)} TikTok videos",
                    items_count=len(data)
                )
            else:
                # API returned nothing - use mock
                mock_data = self.get_mock_data(query, limit=limit)
                return ConnectorResult(
                    status=ConnectorStatus.PARTIAL,
                    data=mock_data,
                    source=self.name,
                    message="TikTok API returned no results - using sample data",
                    items_count=len(mock_data)
                )
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"TikTok API error: {e}")
            
            mock_data = self.get_mock_data(query, limit=limit)
            
            # Check for specific errors
            if "403" in error_msg or "access" in error_msg.lower():
                return ConnectorResult(
                    status=ConnectorStatus.FAILED,
                    data=mock_data,
                    source=self.name,
                    message="TikTok Research API access not approved - using sample data",
                    items_count=len(mock_data),
                    error_detail="Requires TikTok Research API approval"
                )
            
            if "429" in error_msg or "rate" in error_msg.lower():
                return ConnectorResult(
                    status=ConnectorStatus.RATE_LIMITED,
                    data=mock_data,
                    source=self.name,
                    message="TikTok rate limited - using sample data",
                    items_count=len(mock_data),
                    error_detail=error_msg
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=mock_data,
                source=self.name,
                message="TikTok unavailable - using sample data",
                items_count=len(mock_data),
                error_detail=f"{type(e).__name__}: {error_msg}"
            )
    
    async def _get_access_token(self):
        """
        Get OAuth access token from TikTok.
        
        Uses client credentials flow.
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required")
        
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(url, data=data, timeout=10)
        )
        
        response.raise_for_status()
        result = response.json()
        
        self._access_token = result.get("access_token")
        self.logger.info("TikTok access token obtained")
    
    async def _search_videos(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search TikTok videos using Research API.
        
        Note: This requires approved Research API access.
        Most developers won't have this.
        """
        if not self._access_token:
            raise ValueError("No access token")
        
        url = "https://open.tiktokapis.com/v2/research/video/query/"
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        
        # Research API query format
        payload = {
            "query": {
                "and": [
                    {"field_name": "keyword", "field_values": [query]}
                ]
            },
            "max_count": limit,
            "fields": [
                "id", "create_time", "username", "region_code",
                "video_description", "music_id", "like_count",
                "comment_count", "share_count", "view_count"
            ]
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(url, json=payload, headers=headers, timeout=15)
        )
        
        response.raise_for_status()
        result = response.json()
        
        videos = []
        for video in result.get("data", {}).get("videos", []):
            videos.append({
                "id": video.get("id", ""),
                "description": video.get("video_description", ""),
                "username": video.get("username", ""),
                "create_time": video.get("create_time", ""),
                "likes": video.get("like_count", 0),
                "comments": video.get("comment_count", 0),
                "shares": video.get("share_count", 0),
                "views": video.get("view_count", 0),
                "region": video.get("region_code", ""),
                "url": f"https://www.tiktok.com/@{video.get('username', '')}/video/{video.get('id', '')}",
                "source": "tiktok_api"
            })
        
        return videos
    
    async def fetch_trending(self, region: str = "US") -> ConnectorResult:
        """
        Fetch trending hashtags/content.
        
        Uses TikTok Creative Center if available.
        """
        # Creative Center doesn't have a public API
        # Would need to scrape or use internal APIs
        
        self.logger.info("Trending data requires Creative Center access")
        
        mock_data = self._get_trending_mock(region)
        return ConnectorResult(
            status=ConnectorStatus.PARTIAL,
            data=mock_data,
            source=self.name,
            message=f"Trending data for {region} (sample)",
            items_count=len(mock_data)
        )
    
    def _get_trending_mock(self, region: str) -> List[Dict[str, Any]]:
        """Generate mock trending data"""
        trends = [
            {"hashtag": "#marketing", "views": "15.2B", "trend": "stable"},
            {"hashtag": "#smallbusiness", "views": "8.7B", "trend": "rising"},
            {"hashtag": "#digitalmarketing", "views": "5.3B", "trend": "rising"},
            {"hashtag": "#socialmedia", "views": "12.1B", "trend": "stable"},
            {"hashtag": "#entrepreneur", "views": "9.8B", "trend": "stable"},
        ]
        return trends
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return mock TikTok data.
        
        Simulates what real TikTok data would look like.
        """
        limit = kwargs.get("limit", 20)
        
        # Try existing mock
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from api_connectors_mock import MockTikTokConnector
            mock = MockTikTokConnector()
            return mock.search_content(query, limit=limit)
        except ImportError:
            pass
        
        # Generate mock data
        usernames = ["creator1", "marketer_pro", "small_biz_tips", "trend_watcher", "digital_guru"]
        hashtags = ["#marketing", "#fyp", "#business", "#tips", "#viral"]
        
        mock_videos = []
        for i in range(min(limit, 10)):
            mock_videos.append({
                "id": f"mock_video_{i}",
                "description": f"Video about {query} {hashtags[i % len(hashtags)]} #{query.replace(' ', '')}",
                "username": usernames[i % len(usernames)],
                "create_time": datetime.now(timezone.utc).isoformat(),
                "likes": (i + 1) * 10000,
                "comments": (i + 1) * 500,
                "shares": (i + 1) * 200,
                "views": (i + 1) * 100000,
                "url": f"https://www.tiktok.com/@{usernames[i % len(usernames)]}/video/mock{i}",
                "source": "mock"
            })
        
        return mock_videos


# Register connector
def _register():
    try:
        from . import register_connector
        register_connector("tiktok", TikTokConnector)
    except ImportError:
        pass

_register()
