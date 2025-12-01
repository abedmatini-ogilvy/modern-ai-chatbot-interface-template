"""
Web Search Connector

Supports multiple search engines with automatic fallback:
1. SerpAPI (Primary) - 100 free searches/month
2. Brave Search (Backup) - 2,000 free searches/month

Why Multiple Providers?
- Redundancy: If one fails, use the other
- Free tier optimization: Use different services to maximize free quota
- Result diversity: Different engines may return different results

Environment Variables:
- SERPAPI_API_KEY: Get from https://serpapi.com/
- BRAVE_SEARCH_API_KEY: Get from https://brave.com/search/api/
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

# Optional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    GoogleSearch = None


class WebSearchConnector(BaseConnector):
    """
    Connector for web search results.
    
    Supports multiple search providers:
    - SerpAPI: Google search results (100/month free)
    - Brave Search: Privacy-focused search (2000/month free)
    
    Falls back between providers automatically.
    
    Usage:
        connector = WebSearchConnector()
        
        # Search with auto provider selection
        result = await connector.fetch("marketing trends 2024")
        
        # Force specific provider
        result = await connector.fetch("query", provider="brave")
    """
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def display_name(self) -> str:
        return "Web Search"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Web Search connector.
        
        Will use whichever API keys are available.
        """
        super().__init__(config)
        
        # Get API keys
        self.serpapi_key = (
            self.config.get("serpapi_key") or
            os.getenv("SERPAPI_API_KEY")
        )
        self.brave_key = (
            self.config.get("brave_key") or
            os.getenv("BRAVE_SEARCH_API_KEY")
        )
        
        # Determine available providers
        self.providers = []
        if SERPAPI_AVAILABLE and self.serpapi_key:
            self.providers.append("serpapi")
        if REQUESTS_AVAILABLE and self.brave_key:
            self.providers.append("brave")
        
        if self.providers:
            self.logger.info(f"Web search providers available: {', '.join(self.providers)}")
    
    def is_configured(self) -> bool:
        """At least one search provider must be configured"""
        return len(self.providers) > 0
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured search providers"""
        return self.providers.copy()
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Search the web using available providers.
        
        Args:
            query: Search query
            limit: Max results (default: 20)
            provider: Force specific provider ("serpapi" or "brave")
            
        Returns:
            ConnectorResult with search results
        """
        limit = kwargs.get("limit", 20)
        preferred_provider = kwargs.get("provider")
        
        # Determine provider order
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try = [preferred_provider]
        else:
            providers_to_try = self.providers.copy()
        
        # Try each provider
        for provider in providers_to_try:
            try:
                if provider == "serpapi":
                    result = await self._fetch_serpapi(query, limit)
                elif provider == "brave":
                    result = await self._fetch_brave(query, limit)
                else:
                    continue
                
                if result.status == ConnectorStatus.SUCCESS:
                    return result
                    
            except Exception as e:
                self.logger.warning(f"{provider} failed: {e}")
                continue
        
        # All providers failed
        return ConnectorResult(
            status=ConnectorStatus.FAILED,
            data=self.get_mock_data(query, limit=limit),
            source=self.name,
            message="All search providers unavailable - using sample data",
            items_count=0
        )
    
    async def _fetch_serpapi(self, query: str, limit: int) -> ConnectorResult:
        """
        Fetch from SerpAPI (Google search results).
        
        SerpAPI provides parsed Google search results.
        Free tier: 100 searches/month
        """
        try:
            # Run synchronous SerpAPI in thread pool
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._serpapi_search_sync(query, limit)
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} results from Google (SerpAPI)",
                items_count=len(data)
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"SerpAPI error: {e}")
            
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return ConnectorResult(
                    status=ConnectorStatus.RATE_LIMITED,
                    data=[],
                    source=self.name,
                    message="SerpAPI monthly quota exceeded",
                    items_count=0,
                    error_detail=error_msg
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=f"SerpAPI error: {error_msg}",
                items_count=0,
                error_detail=error_msg
            )
    
    def _serpapi_search_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Synchronous SerpAPI search"""
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": limit,
            "hl": "en",
            "gl": "us"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        data = []
        for item in results.get("organic_results", [])[:limit]:
            data.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position", 0),
                "displayed_link": item.get("displayed_link", ""),
                "source": "serpapi",
                "engine": "google"
            })
        
        return data
    
    async def _fetch_brave(self, query: str, limit: int) -> ConnectorResult:
        """
        Fetch from Brave Search API.
        
        Brave is privacy-focused and has generous free tier.
        Free tier: 2,000 searches/month
        """
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._brave_search_sync(query, limit)
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} results from Brave Search",
                items_count=len(data)
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Brave Search error: {e}")
            
            if "429" in error_msg or "rate" in error_msg.lower():
                return ConnectorResult(
                    status=ConnectorStatus.RATE_LIMITED,
                    data=[],
                    source=self.name,
                    message="Brave Search rate limited",
                    items_count=0,
                    error_detail=error_msg
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=f"Brave Search error: {error_msg}",
                items_count=0,
                error_detail=error_msg
            )
    
    def _brave_search_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Synchronous Brave Search"""
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.brave_key
        }
        
        params = {
            "q": query,
            "count": limit,
            "text_decorations": False,
            "search_lang": "en",
            "country": "us"
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        
        results = response.json()
        data = []
        
        for item in results.get("web", {}).get("results", [])[:limit]:
            data.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "age": item.get("age", ""),
                "source": "brave",
                "engine": "brave"
            })
        
        return data
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Return mock search results"""
        limit = kwargs.get("limit", 10)
        
        # Try existing mock
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from api_connectors_mock import MockWebSearchConnector
            mock = MockWebSearchConnector()
            return mock.search(query, limit=limit)
        except ImportError:
            pass
        
        # Generate mock data
        domains = ["example.com", "blog.example.org", "news.site.com", "research.edu"]
        mock_results = []
        
        for i in range(min(limit, 10)):
            mock_results.append({
                "title": f"Article about {query} - Result #{i+1}",
                "url": f"https://{domains[i % len(domains)]}/{query.replace(' ', '-')}-{i}",
                "snippet": f"This is a sample search result about {query}. Learn more about trends and insights.",
                "position": i + 1,
                "source": "mock",
                "engine": "mock"
            })
        
        return mock_results


# Register connector
def _register():
    try:
        from . import register_connector
        register_connector("web_search", WebSearchConnector)
    except ImportError:
        pass

_register()
