# API Connectors Architecture

> **Purpose**: Technical design for modular, testable API connectors  
> **Last Updated**: November 2024

---

## 📐 Design Principles

1. **Single Responsibility**: Each connector handles one data source
2. **Fail Gracefully**: Return mock data on API failure
3. **Transparent Errors**: Always tell user what failed and why
4. **Testable**: Each connector independently testable
5. **Configurable**: Enable/disable via environment variables
6. **Cacheable**: Support caching at connector level

---

## 🏗️ Base Connector Interface

All connectors inherit from `BaseConnector`:

```python
# connectors/base_connector.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class ConnectorStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"  # Some data retrieved
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"

@dataclass
class ConnectorResult:
    """Standard result format for all connectors"""
    status: ConnectorStatus
    data: List[Dict[str, Any]]
    source: str
    message: str
    items_count: int
    cached: bool = False
    error_detail: Optional[str] = None

class BaseConnector(ABC):
    """Abstract base class for all API connectors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {}
        self._enabled = True
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique connector name (e.g., 'twitter', 'reddit')"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI"""
        pass
    
    @abstractmethod
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch data from the API
        
        Args:
            query: Search query string
            **kwargs: Additional parameters (limit, date_range, etc.)
            
        Returns:
            ConnectorResult with status and data
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if required credentials are available"""
        pass
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        """Return mock data as fallback"""
        return []
    
    async def fetch_with_fallback(self, query: str, **kwargs) -> ConnectorResult:
        """Fetch real data, fall back to mock on failure"""
        if not self._enabled:
            return ConnectorResult(
                status=ConnectorStatus.DISABLED,
                data=[],
                source=self.name,
                message=f"{self.display_name} is disabled",
                items_count=0
            )
        
        if not self.is_configured():
            self.logger.warning(f"{self.name} not configured, using mock data")
            mock_data = self.get_mock_data(query)
            return ConnectorResult(
                status=ConnectorStatus.PARTIAL,
                data=mock_data,
                source=self.name,
                message=f"{self.display_name} not configured - using sample data",
                items_count=len(mock_data)
            )
        
        try:
            return await self.fetch(query, **kwargs)
        except Exception as e:
            self.logger.error(f"{self.name} fetch failed: {e}")
            mock_data = self.get_mock_data(query)
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=mock_data,
                source=self.name,
                message=f"{self.display_name} unavailable - using sample data",
                items_count=len(mock_data),
                error_detail=str(e)
            )
```

---

## 📁 Connector Implementations

### Twitter Connector

```python
# connectors/twitter_connector.py

import os
from typing import Dict, List, Any
import tweepy
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class TwitterConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "twitter"
    
    @property
    def display_name(self) -> str:
        return "Twitter/X"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = None
        if self.bearer_token:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
    
    def is_configured(self) -> bool:
        return bool(self.bearer_token)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        limit = kwargs.get("limit", 50)
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # Twitter max is 100
                tweet_fields=["created_at", "public_metrics", "author_id"]
            )
            
            if not tweets.data:
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=[],
                    source=self.name,
                    message="No tweets found for this query",
                    items_count=0
                )
            
            data = []
            for tweet in tweets.data:
                data.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": str(tweet.created_at),
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "author_id": tweet.author_id
                })
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} tweets",
                items_count=len(data)
            )
            
        except tweepy.TooManyRequests:
            return ConnectorResult(
                status=ConnectorStatus.RATE_LIMITED,
                data=self.get_mock_data(query),
                source=self.name,
                message="Twitter rate limit reached - using sample data",
                items_count=0,
                error_detail="Monthly quota may be exhausted"
            )
        except tweepy.Unauthorized:
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query),
                source=self.name,
                message="Twitter authentication failed",
                items_count=0,
                error_detail="Check TWITTER_BEARER_TOKEN"
            )
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        # Import from existing mock connector
        from api_connectors_mock import MockTwitterConnector
        return MockTwitterConnector().search_tweets(query, limit=20)
```

### Reddit Connector

```python
# connectors/reddit_connector.py

import os
from typing import Dict, List, Any
import praw
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class RedditConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "reddit"
    
    @property
    def display_name(self) -> str:
        return "Reddit"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "TrendResearchBot/1.0")
        self.reddit = None
        
        if self.is_configured():
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
    
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        limit = kwargs.get("limit", 50)
        subreddit = kwargs.get("subreddit", "all")
        
        try:
            data = []
            
            # Search posts
            for post in self.reddit.subreddit(subreddit).search(query, limit=limit):
                data.append({
                    "id": post.id,
                    "title": post.title,
                    "text": post.selftext[:500] if post.selftext else "",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "subreddit": str(post.subreddit),
                    "created_utc": post.created_utc,
                    "url": f"https://reddit.com{post.permalink}",
                    "type": "post"
                })
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} Reddit posts",
                items_count=len(data)
            )
            
        except Exception as e:
            self.logger.error(f"Reddit error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query),
                source=self.name,
                message=f"Reddit search failed - using sample data",
                items_count=0,
                error_detail=str(e)
            )
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        from api_connectors_mock import MockRedditConnector
        return MockRedditConnector().search_posts(query, limit=20)
```

### Google Trends Connector

```python
# connectors/google_trends_connector.py

import os
from typing import Dict, List, Any
from pytrends.request import TrendReq
import time
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class GoogleTrendsConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "google_trends"
    
    @property
    def display_name(self) -> str:
        return "Google Trends"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    def is_configured(self) -> bool:
        # pytrends doesn't need API key
        return True
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        timeframe = kwargs.get("timeframe", "today 3-m")  # Last 3 months
        
        try:
            # Split query into keywords (max 5)
            keywords = [kw.strip() for kw in query.split(",")[:5]]
            if len(keywords) == 1:
                keywords = query.split()[:5]
            
            self.pytrends.build_payload(keywords, timeframe=timeframe)
            
            # Get interest over time
            time.sleep(1)  # Rate limit protection
            interest_df = self.pytrends.interest_over_time()
            
            # Get related queries
            time.sleep(1)
            related = self.pytrends.related_queries()
            
            data = {
                "interest_over_time": interest_df.to_dict() if not interest_df.empty else {},
                "related_queries": {},
                "keywords": keywords
            }
            
            # Process related queries
            for keyword in keywords:
                if keyword in related and related[keyword]["top"] is not None:
                    data["related_queries"][keyword] = {
                        "top": related[keyword]["top"].to_dict("records")[:10],
                        "rising": related[keyword]["rising"].to_dict("records")[:10] 
                            if related[keyword]["rising"] is not None else []
                    }
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=[data],  # Single item with all trend data
                source=self.name,
                message=f"Retrieved trends for {len(keywords)} keywords",
                items_count=len(keywords)
            )
            
        except Exception as e:
            self.logger.error(f"Google Trends error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query),
                source=self.name,
                message="Google Trends unavailable - using sample data",
                items_count=0,
                error_detail=str(e)
            )
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        from api_connectors_mock import MockGoogleTrendsConnector
        return [MockGoogleTrendsConnector().get_trends(query)]
```

### Web Search Connector

```python
# connectors/web_search_connector.py

import os
from typing import Dict, List, Any
import requests
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class WebSearchConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def display_name(self) -> str:
        return "Web Search"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    
    def is_configured(self) -> bool:
        return bool(self.serpapi_key or self.brave_key)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        limit = kwargs.get("limit", 20)
        
        # Try SerpAPI first, then Brave
        if self.serpapi_key:
            result = await self._fetch_serpapi(query, limit)
            if result.status == ConnectorStatus.SUCCESS:
                return result
        
        if self.brave_key:
            result = await self._fetch_brave(query, limit)
            if result.status == ConnectorStatus.SUCCESS:
                return result
        
        # Both failed
        return ConnectorResult(
            status=ConnectorStatus.FAILED,
            data=self.get_mock_data(query),
            source=self.name,
            message="Web search unavailable - using sample data",
            items_count=0
        )
    
    async def _fetch_serpapi(self, query: str, limit: int) -> ConnectorResult:
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": limit
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            data = []
            for item in results.get("organic_results", [])[:limit]:
                data.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "serpapi"
                })
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} search results (SerpAPI)",
                items_count=len(data)
            )
        except Exception as e:
            self.logger.error(f"SerpAPI error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=str(e),
                items_count=0
            )
    
    async def _fetch_brave(self, query: str, limit: int) -> ConnectorResult:
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_key
            }
            params = {"q": query, "count": limit}
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            data = []
            
            for item in results.get("web", {}).get("results", [])[:limit]:
                data.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "source": "brave"
                })
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=data,
                source=self.name,
                message=f"Retrieved {len(data)} search results (Brave)",
                items_count=len(data)
            )
        except Exception as e:
            self.logger.error(f"Brave Search error: {e}")
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=str(e),
                items_count=0
            )
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        from api_connectors_mock import MockWebSearchConnector
        return MockWebSearchConnector().search(query, limit=20)
```

### TikTok Connector

```python
# connectors/tiktok_connector.py

import os
from typing import Dict, List, Any
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class TikTokConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "tiktok"
    
    @property
    def display_name(self) -> str:
        return "TikTok"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    
    def is_configured(self) -> bool:
        return bool(self.client_key and self.client_secret)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        # TikTok API implementation
        # Note: TikTok API access is limited, may need to use mock data
        
        if not self.is_configured():
            return ConnectorResult(
                status=ConnectorStatus.PARTIAL,
                data=self.get_mock_data(query),
                source=self.name,
                message="TikTok API not configured - using sample data",
                items_count=0
            )
        
        try:
            # Placeholder for actual TikTok API implementation
            # TikTok Research API requires business account approval
            
            return ConnectorResult(
                status=ConnectorStatus.PARTIAL,
                data=self.get_mock_data(query),
                source=self.name,
                message="TikTok API access pending - using sample data",
                items_count=0
            )
            
        except Exception as e:
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=self.get_mock_data(query),
                source=self.name,
                message="TikTok unavailable - using sample data",
                items_count=0,
                error_detail=str(e)
            )
    
    def get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        from api_connectors_mock import MockTikTokConnector
        return MockTikTokConnector().search_content(query, limit=20)
```

### LLM Connector

```python
# connectors/llm_connector.py

import os
from typing import Dict, List, Any, Optional
from enum import Enum
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

class LLMProvider(Enum):
    GEMINI = "gemini"
    AZURE_OPENAI = "azure"
    # Add more providers as needed

class LLMConnector(BaseConnector):
    
    @property
    def name(self) -> str:
        return "llm"
    
    @property
    def display_name(self) -> str:
        return "AI Analysis"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        # Gemini config
        self.gemini_key = os.getenv("GOOGLE_AI_API_KEY")
        
        # Azure OpenAI config
        self.azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    def is_configured(self) -> bool:
        return bool(self.gemini_key or (self.azure_key and self.azure_endpoint))
    
    def get_available_providers(self) -> List[str]:
        """Return list of configured providers"""
        providers = []
        if self.gemini_key:
            providers.append("gemini")
        if self.azure_key and self.azure_endpoint:
            providers.append("azure")
        return providers
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """Not used for LLM - use analyze() instead"""
        raise NotImplementedError("Use analyze() method for LLM")
    
    async def analyze(
        self, 
        data: Dict[str, Any], 
        prompt_type: str = "analysis",
        provider: Optional[str] = None
    ) -> ConnectorResult:
        """
        Analyze collected data using LLM
        
        Args:
            data: Collected research data from all sources
            prompt_type: Type of analysis ("analysis", "summary", "recommendations")
            provider: Specific LLM provider to use (default: configured default)
        """
        provider = provider or self.default_provider
        
        if provider == "gemini" and self.gemini_key:
            return await self._analyze_gemini(data, prompt_type)
        elif provider == "azure" and self.azure_key:
            return await self._analyze_azure(data, prompt_type)
        else:
            return await self._analyze_mock(data, prompt_type)
    
    async def _analyze_gemini(self, data: Dict, prompt_type: str) -> ConnectorResult:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self._build_prompt(data, prompt_type)
            response = model.generate_content(prompt)
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=[{"analysis": response.text, "provider": "gemini"}],
                source=self.name,
                message="Analysis complete (Gemini)",
                items_count=1
            )
        except Exception as e:
            self.logger.error(f"Gemini error: {e}")
            return await self._analyze_mock(data, prompt_type)
    
    async def _analyze_azure(self, data: Dict, prompt_type: str) -> ConnectorResult:
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=self.azure_key,
                api_version="2024-02-15-preview",
                azure_endpoint=self.azure_endpoint
            )
            
            prompt = self._build_prompt(data, prompt_type)
            
            response = client.chat.completions.create(
                model=self.azure_deployment,
                messages=[
                    {"role": "system", "content": "You are a marketing research analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=[{"analysis": response.choices[0].message.content, "provider": "azure"}],
                source=self.name,
                message="Analysis complete (Azure OpenAI)",
                items_count=1
            )
        except Exception as e:
            self.logger.error(f"Azure OpenAI error: {e}")
            return await self._analyze_mock(data, prompt_type)
    
    async def _analyze_mock(self, data: Dict, prompt_type: str) -> ConnectorResult:
        """Generate mock analysis when LLM is unavailable"""
        mock_analysis = {
            "analysis": f"""
## Research Analysis (Sample)

Based on the collected data, here are the key insights:

### Summary
- Analyzed {sum(len(v) if isinstance(v, list) else 1 for v in data.values())} data points
- Sources: {', '.join(data.keys())}

### Key Findings
1. Strong engagement patterns observed across social platforms
2. Rising interest in the research topic
3. Multiple discussion threads indicate growing awareness

### Recommendations
1. Focus on high-engagement platforms
2. Monitor trending conversations
3. Consider timing of content publication

*Note: This is sample analysis. Configure LLM API keys for real insights.*
            """,
            "provider": "mock"
        }
        
        return ConnectorResult(
            status=ConnectorStatus.PARTIAL,
            data=[mock_analysis],
            source=self.name,
            message="Using sample analysis - configure LLM for real insights",
            items_count=1
        )
    
    def _build_prompt(self, data: Dict, prompt_type: str) -> str:
        """Build analysis prompt based on type"""
        
        data_summary = self._summarize_data(data)
        
        prompts = {
            "analysis": f"""
Analyze this marketing research data and provide insights:

{data_summary}

Provide:
1. Executive Summary (2-3 sentences)
2. Key Findings (5-7 bullet points)
3. Trend Analysis
4. Recommendations (3-5 actionable items)
            """,
            "summary": f"""
Summarize this research data concisely:

{data_summary}

Provide a 3-paragraph summary covering main themes and insights.
            """,
            "recommendations": f"""
Based on this research data, provide strategic recommendations:

{data_summary}

List 5-7 specific, actionable recommendations for a marketing team.
            """
        }
        
        return prompts.get(prompt_type, prompts["analysis"])
    
    def _summarize_data(self, data: Dict) -> str:
        """Create a text summary of collected data for the LLM prompt"""
        parts = []
        
        for source, items in data.items():
            if isinstance(items, list) and items:
                parts.append(f"\n### {source.upper()} ({len(items)} items)")
                for item in items[:10]:  # Limit to prevent token overflow
                    if isinstance(item, dict):
                        text = item.get("text") or item.get("title") or item.get("snippet") or str(item)
                        parts.append(f"- {text[:200]}")
        
        return "\n".join(parts)
```

---

## 🔧 Connector Factory

```python
# connectors/__init__.py

from typing import Dict, Type
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus
from .twitter_connector import TwitterConnector
from .reddit_connector import RedditConnector
from .google_trends_connector import GoogleTrendsConnector
from .web_search_connector import WebSearchConnector
from .tiktok_connector import TikTokConnector
from .llm_connector import LLMConnector, LLMProvider

# Registry of all connectors
CONNECTORS: Dict[str, Type[BaseConnector]] = {
    "twitter": TwitterConnector,
    "reddit": RedditConnector,
    "google_trends": GoogleTrendsConnector,
    "web_search": WebSearchConnector,
    "tiktok": TikTokConnector,
}

def get_connector(name: str, config: Dict = None) -> BaseConnector:
    """Factory function to get connector by name"""
    if name not in CONNECTORS:
        raise ValueError(f"Unknown connector: {name}")
    return CONNECTORS[name](config)

def get_all_connectors(config: Dict = None) -> Dict[str, BaseConnector]:
    """Get instances of all connectors"""
    return {name: cls(config) for name, cls in CONNECTORS.items()}

def get_llm_connector(config: Dict = None) -> LLMConnector:
    """Get LLM connector instance"""
    return LLMConnector(config)

__all__ = [
    "BaseConnector",
    "ConnectorResult", 
    "ConnectorStatus",
    "TwitterConnector",
    "RedditConnector",
    "GoogleTrendsConnector",
    "WebSearchConnector",
    "TikTokConnector",
    "LLMConnector",
    "LLMProvider",
    "CONNECTORS",
    "get_connector",
    "get_all_connectors",
    "get_llm_connector",
]
```

---

## 🧪 Testing Structure

```python
# connectors/tests/test_twitter.py

import pytest
from unittest.mock import patch, MagicMock
from connectors.twitter_connector import TwitterConnector
from connectors.base_connector import ConnectorStatus

class TestTwitterConnector:
    
    def test_name(self):
        connector = TwitterConnector()
        assert connector.name == "twitter"
        assert connector.display_name == "Twitter/X"
    
    def test_not_configured_without_token(self):
        with patch.dict('os.environ', {}, clear=True):
            connector = TwitterConnector()
            assert not connector.is_configured()
    
    def test_configured_with_token(self):
        with patch.dict('os.environ', {'TWITTER_BEARER_TOKEN': 'test_token'}):
            connector = TwitterConnector()
            assert connector.is_configured()
    
    @pytest.mark.asyncio
    async def test_fetch_with_fallback_when_not_configured(self):
        with patch.dict('os.environ', {}, clear=True):
            connector = TwitterConnector()
            result = await connector.fetch_with_fallback("test query")
            assert result.status == ConnectorStatus.PARTIAL
            assert "not configured" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_returns_data(self):
        with patch.dict('os.environ', {'TWITTER_BEARER_TOKEN': 'test_token'}):
            connector = TwitterConnector()
            
            # Mock tweepy client
            mock_tweet = MagicMock()
            mock_tweet.id = "123"
            mock_tweet.text = "Test tweet"
            mock_tweet.created_at = "2024-01-01"
            mock_tweet.public_metrics = {"like_count": 10, "retweet_count": 5}
            mock_tweet.author_id = "456"
            
            mock_response = MagicMock()
            mock_response.data = [mock_tweet]
            
            with patch.object(connector.client, 'search_recent_tweets', return_value=mock_response):
                result = await connector.fetch("test query")
                assert result.status == ConnectorStatus.SUCCESS
                assert len(result.data) == 1
                assert result.data[0]["text"] == "Test tweet"
```

---

## 📊 Integration with Research Service

Update `research_service.py` to use new connectors:

```python
# services/research_service.py (updated)

from connectors import (
    get_all_connectors,
    get_llm_connector,
    ConnectorStatus
)

class ResearchService:
    
    def __init__(self):
        self.connectors = get_all_connectors()
        self.llm = get_llm_connector()
    
    async def run_research(self, question: str, search_terms: List[str]) -> Dict:
        results = {}
        statuses = {}
        
        # Collect data from all connectors in parallel
        query = " ".join(search_terms)
        
        for name, connector in self.connectors.items():
            result = await connector.fetch_with_fallback(query)
            results[name] = result.data
            statuses[name] = {
                "status": result.status.value,
                "message": result.message,
                "count": result.items_count
            }
        
        # Analyze with LLM
        llm_result = await self.llm.analyze(results, prompt_type="analysis")
        
        return {
            "data": results,
            "analysis": llm_result.data[0]["analysis"],
            "llm_provider": llm_result.data[0]["provider"],
            "source_statuses": statuses
        }
```

---

## 🎯 Key Benefits of This Architecture

1. **Modular**: Each connector is independent, easy to add/remove
2. **Testable**: Mock dependencies, test each connector in isolation
3. **Resilient**: Automatic fallback to mock data
4. **Transparent**: Clear status messages for users
5. **Extensible**: Easy to add new providers (search engines, LLMs)
6. **Configurable**: Enable/disable via environment variables
7. **Type-safe**: Consistent `ConnectorResult` format
