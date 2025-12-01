"""
Google Trends Connector

Uses pytrends library to fetch Google Trends data.

KEY POINT: NO API KEY REQUIRED!
pytrends works by scraping Google Trends, not via official API.

Features:
- Interest over time (search volume trends)
- Related queries (what else people search)
- Rising queries (trending searches)
- Regional interest by country/region

Limitations:
- Google may rate-limit or block if overused
- Data is relative (0-100 scale), not absolute search volume
- Max 5 keywords per request
- Only shows data where there's enough search volume

Environment Variables:
- None required!

Best Practices:
- Add delays between requests (1-2 seconds)
- Cache results aggressively
- Limit to 5 keywords max per request
"""

import os
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

# pytrends is optional
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    TrendReq = None


class GoogleTrendsConnector(BaseConnector):
    """
    Connector for Google Trends data using pytrends.
    
    This is one of the few connectors that doesn't need API keys!
    It works by making requests to Google Trends website.
    
    Usage:
        connector = GoogleTrendsConnector()
        
        # Get trends for keywords
        result = await connector.fetch("marketing, social media, TikTok")
        
        # Access trend data
        if result.is_success:
            trends = result.data[0]
            print(trends["interest_over_time"])
            print(trends["related_queries"])
    
    Note: Returns data in a different format than other connectors.
    Instead of a list of items, returns a single dict with trend data.
    """
    
    @property
    def name(self) -> str:
        return "google_trends"
    
    @property
    def display_name(self) -> str:
        return "Google Trends"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Google Trends connector.
        
        Config options:
        - hl: Language (default: "en-US")
        - tz: Timezone offset (default: 360 = CST)
        - geo: Country code (default: "" = worldwide)
        - retries: Number of retries (default: 3)
        """
        super().__init__(config)
        
        self.hl = self.config.get("hl", "en-US")
        self.tz = self.config.get("tz", 360)  # Timezone offset
        self.geo = self.config.get("geo", "")  # Empty = worldwide
        self.retries = self.config.get("retries", 3)
        
        # pytrends client (created fresh for each request to avoid session issues)
        self._pytrends = None
    
    def is_configured(self) -> bool:
        """
        Google Trends doesn't need API keys!
        Just check if pytrends is installed.
        """
        if not PYTRENDS_AVAILABLE:
            self.logger.warning("pytrends not installed. Run: pip install pytrends")
            return False
        return True
    
    def _get_client(self) -> 'TrendReq':
        """
        Get or create pytrends client.
        
        Create fresh client to avoid session/cookie issues.
        """
        return TrendReq(
            hl=self.hl,
            tz=self.tz,
            retries=self.retries,
            backoff_factor=0.5
        )
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch Google Trends data for keywords.
        
        Args:
            query: Keywords (comma-separated, max 5)
                   e.g., "marketing, social media, TikTok"
            timeframe: Time range (default: "today 3-m")
                      Options: "now 1-H", "now 4-H", "now 1-d", "now 7-d",
                               "today 1-m", "today 3-m", "today 12-m", "today 5-y"
            geo: Country code (e.g., "US", "GB", "NG")
            include_related: Whether to fetch related queries (default: True)
            include_rising: Whether to fetch rising queries (default: True)
            
        Returns:
            ConnectorResult with trend data
        """
        timeframe = kwargs.get("timeframe", "today 3-m")
        geo = kwargs.get("geo", self.geo)
        include_related = kwargs.get("include_related", True)
        include_rising = kwargs.get("include_rising", True)
        
        # Parse keywords (max 5 for Google Trends)
        keywords = self._parse_keywords(query)
        
        if not keywords:
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message="No valid keywords provided",
                items_count=0
            )
        
        try:
            # Run in executor (pytrends is synchronous)
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._fetch_sync(keywords, timeframe, geo, include_related, include_rising)
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=[data],  # Single item with all trend data
                source=self.name,
                message=f"Retrieved trends for {len(keywords)} keywords",
                items_count=len(keywords)
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Google Trends error: {type(e).__name__}: {e}")
            
            # Check for rate limiting
            if "429" in error_msg or "too many" in error_msg.lower():
                return ConnectorResult(
                    status=ConnectorStatus.RATE_LIMITED,
                    data=self.get_mock_data(query),
                    source=self.name,
                    message="Google Trends rate limited - try again later",
                    items_count=0,
                    error_detail=error_msg
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query),
                source=self.name,
                message="Google Trends unavailable - using sample data",
                items_count=0,
                error_detail=f"{type(e).__name__}: {error_msg}"
            )
    
    def _parse_keywords(self, query: str, max_keywords: int = 5) -> List[str]:
        """
        Parse query into list of keywords.
        
        Google Trends accepts max 5 keywords per request.
        """
        # Split by comma or space
        if "," in query:
            keywords = [k.strip() for k in query.split(",")]
        else:
            # If no commas, treat whole query as one keyword
            # (unless it's very long, then split by space)
            if len(query.split()) > 5:
                keywords = query.split()[:max_keywords]
            else:
                keywords = [query]
        
        # Filter empty and limit to max
        keywords = [k for k in keywords if k.strip()][:max_keywords]
        
        return keywords
    
    def _fetch_sync(
        self,
        keywords: List[str],
        timeframe: str,
        geo: str,
        include_related: bool,
        include_rising: bool
    ) -> Dict[str, Any]:
        """
        Synchronous fetch of trend data.
        
        This makes multiple API calls:
        1. Build payload
        2. Interest over time
        3. Related queries (optional)
        """
        pytrends = self._get_client()
        
        # Build the payload (sets up the query)
        pytrends.build_payload(
            keywords,
            timeframe=timeframe,
            geo=geo
        )
        
        result = {
            "keywords": keywords,
            "timeframe": timeframe,
            "geo": geo or "worldwide",
            "interest_over_time": {},
            "related_queries": {},
            "interest_by_region": {}
        }
        
        # 1. Get interest over time
        time.sleep(0.5)  # Rate limit protection
        try:
            iot_df = pytrends.interest_over_time()
            if not iot_df.empty:
                # Convert DataFrame to dict
                result["interest_over_time"] = {
                    "dates": iot_df.index.strftime("%Y-%m-%d").tolist(),
                    "values": {}
                }
                for keyword in keywords:
                    if keyword in iot_df.columns:
                        result["interest_over_time"]["values"][keyword] = iot_df[keyword].tolist()
                
                # Add summary statistics
                result["interest_over_time"]["summary"] = {
                    keyword: {
                        "avg": round(iot_df[keyword].mean(), 1),
                        "max": int(iot_df[keyword].max()),
                        "min": int(iot_df[keyword].min()),
                        "current": int(iot_df[keyword].iloc[-1]) if len(iot_df) > 0 else 0
                    }
                    for keyword in keywords if keyword in iot_df.columns
                }
        except Exception as e:
            error_msg = str(e)
            # Re-raise rate limit errors
            if "429" in error_msg or "too many" in error_msg.lower():
                raise
            self.logger.warning(f"Failed to get interest over time: {e}")
        
        # 2. Get related queries
        if include_related:
            time.sleep(0.5)
            try:
                related = pytrends.related_queries()
                for keyword in keywords:
                    if keyword in related and related[keyword] is not None:
                        top_df = related[keyword].get("top")
                        rising_df = related[keyword].get("rising")
                        
                        result["related_queries"][keyword] = {
                            "top": top_df.to_dict("records")[:10] if top_df is not None and not top_df.empty else [],
                            "rising": rising_df.to_dict("records")[:10] if rising_df is not None and not rising_df.empty else []
                        }
            except Exception as e:
                self.logger.warning(f"Failed to get related queries: {e}")
        
        # 3. Get interest by region (optional, slower)
        try:
            time.sleep(0.5)
            region_df = pytrends.interest_by_region(resolution='COUNTRY')
            if not region_df.empty:
                # Get top 10 regions per keyword
                for keyword in keywords:
                    if keyword in region_df.columns:
                        top_regions = region_df[keyword].nlargest(10)
                        result["interest_by_region"][keyword] = {
                            region: int(value) 
                            for region, value in top_regions.items() 
                            if value > 0
                        }
        except Exception as e:
            self.logger.warning(f"Failed to get interest by region: {e}")
        
        return result
    
    async def fetch_trending_searches(self, geo: str = "united_states") -> ConnectorResult:
        """
        Fetch currently trending searches.
        
        Args:
            geo: Country for trending searches
                 Options: "united_states", "united_kingdom", "nigeria", etc.
        
        Returns:
            ConnectorResult with trending search terms
        """
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._fetch_trending_sync(geo)
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} trending searches for {geo}",
                items_count=len(data)
            )
        except Exception as e:
            self.logger.error(f"Trending searches error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message="Failed to fetch trending searches",
                items_count=0,
                error_detail=str(e)
            )
    
    def _fetch_trending_sync(self, geo: str) -> List[Dict[str, Any]]:
        """Fetch trending searches synchronously"""
        pytrends = self._get_client()
        
        try:
            df = pytrends.trending_searches(pn=geo)
            return [{"term": term, "rank": i+1} for i, term in enumerate(df[0].tolist())]
        except Exception as e:
            self.logger.warning(f"Trending searches failed: {e}")
            return []
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return mock Google Trends data.
        """
        keywords = self._parse_keywords(query)
        
        # Try existing mock
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from api_connectors_mock import MockGoogleTrendsConnector
            mock = MockGoogleTrendsConnector()
            return [mock.get_trends(query)]
        except ImportError:
            pass
        
        # Generate mock data
        mock_data = {
            "keywords": keywords,
            "timeframe": "today 3-m",
            "geo": "worldwide",
            "interest_over_time": {
                "dates": ["2024-01-01", "2024-02-01", "2024-03-01"],
                "values": {kw: [50, 75, 65] for kw in keywords},
                "summary": {
                    kw: {"avg": 63.3, "max": 75, "min": 50, "current": 65}
                    for kw in keywords
                }
            },
            "related_queries": {
                kw: {
                    "top": [
                        {"query": f"{kw} strategy", "value": 100},
                        {"query": f"{kw} tips", "value": 85},
                        {"query": f"best {kw}", "value": 70}
                    ],
                    "rising": [
                        {"query": f"{kw} 2024", "value": "Breakout"},
                        {"query": f"{kw} AI", "value": "+200%"}
                    ]
                }
                for kw in keywords
            },
            "interest_by_region": {
                kw: {"United States": 85, "United Kingdom": 72, "Nigeria": 65}
                for kw in keywords
            },
            "source": "mock"
        }
        
        return [mock_data]


# Register connector
def _register():
    try:
        from . import register_connector
        register_connector("google_trends", GoogleTrendsConnector)
    except ImportError:
        pass

_register()
