"""
Tests for Reddit Connector

Run tests:
    cd backend
    python -m pytest connectors/tests/test_reddit.py -v
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from connectors.reddit_connector import RedditConnector, PRAW_AVAILABLE
from connectors.base_connector import ConnectorStatus


class TestRedditConnectorBasics:
    """Test basic connector properties"""
    
    def test_name(self):
        connector = RedditConnector()
        assert connector.name == "reddit"
    
    def test_display_name(self):
        connector = RedditConnector()
        assert connector.display_name == "Reddit"
    
    def test_not_configured_without_credentials(self):
        """is_configured returns False without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            connector = RedditConnector()
            # Will be False either due to missing creds or missing praw
            assert connector.is_configured() == False or not PRAW_AVAILABLE
    
    @pytest.mark.skipif(not PRAW_AVAILABLE, reason="praw not installed")
    def test_configured_with_credentials(self):
        """is_configured returns True with credentials"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret"
        }):
            connector = RedditConnector()
            assert connector.is_configured() == True
    
    def test_config_override(self):
        """Config dict can override env variables"""
        connector = RedditConnector(config={
            "client_id": "config_id",
            "client_secret": "config_secret"
        })
        assert connector.client_id == "config_id"
        assert connector.client_secret == "config_secret"
    
    def test_default_user_agent(self):
        """Default user agent is set"""
        connector = RedditConnector()
        assert "TrendResearchBot" in connector.user_agent


class TestRedditConnectorMocking:
    """Test connector with mocked PRAW"""
    
    @pytest.fixture
    def mock_post(self):
        """Create a mock Reddit post"""
        post = MagicMock()
        post.id = "abc123"
        post.title = "Test Post About Marketing"
        post.selftext = "This is the post content about marketing trends."
        post.score = 500
        post.upvote_ratio = 0.95
        post.num_comments = 50
        post.subreddit = MagicMock()
        post.subreddit.__str__ = lambda x: "marketing"
        post.subreddit.subscribers = 100000
        post.author = MagicMock()
        post.author.__str__ = lambda x: "test_author"
        post.created_utc = 1704067200  # 2024-01-01
        post.permalink = "/r/marketing/comments/abc123/test_post/"
        post.is_self = True
        post.url = "https://reddit.com/r/marketing/comments/abc123/test_post/"
        post.total_awards_received = 2
        return post
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRAW_AVAILABLE, reason="praw not installed")
    async def test_fetch_success(self, mock_post):
        """Successful API call returns formatted data"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret"
        }):
            connector = RedditConnector()
            
            # Mock the subreddit search
            mock_subreddit = MagicMock()
            mock_subreddit.search.return_value = [mock_post]
            
            connector.reddit = MagicMock()
            connector.reddit.subreddit.return_value = mock_subreddit
            
            result = await connector.fetch("marketing trends")
            
            assert result.status == ConnectorStatus.SUCCESS
            assert len(result.data) == 1
            assert result.data[0]["title"] == "Test Post About Marketing"
            assert result.data[0]["score"] == 500
            assert result.data[0]["subreddit"] == "marketing"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRAW_AVAILABLE, reason="praw not installed")
    async def test_fetch_empty_results(self):
        """Empty results handled gracefully"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret"
        }):
            connector = RedditConnector()
            
            mock_subreddit = MagicMock()
            mock_subreddit.search.return_value = []
            
            connector.reddit = MagicMock()
            connector.reddit.subreddit.return_value = mock_subreddit
            
            result = await connector.fetch("xyznonexistent123")
            
            assert result.status == ConnectorStatus.SUCCESS
            assert len(result.data) == 0
            assert "No posts found" in result.message
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PRAW_AVAILABLE, reason="praw not installed")
    async def test_search_specific_subreddit(self, mock_post):
        """Can search specific subreddit"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret"
        }):
            connector = RedditConnector()
            
            mock_subreddit = MagicMock()
            mock_subreddit.search.return_value = [mock_post]
            
            connector.reddit = MagicMock()
            connector.reddit.subreddit.return_value = mock_subreddit
            
            result = await connector.fetch("trends", subreddit="marketing")
            
            # Verify subreddit was called with correct name
            connector.reddit.subreddit.assert_called_with("marketing")
            assert result.status == ConnectorStatus.SUCCESS


class TestMockData:
    """Test mock data generation"""
    
    def test_get_mock_data(self):
        """Mock data has expected structure"""
        connector = RedditConnector()
        mock_data = connector.get_mock_data("marketing", limit=5)
        
        assert len(mock_data) <= 5
        assert len(mock_data) > 0
        
        post = mock_data[0]
        assert "id" in post
        assert "title" in post
        assert "score" in post
        assert "subreddit" in post


class TestFetchWithFallback:
    """Test the full fallback chain"""
    
    @pytest.mark.asyncio
    async def test_not_configured_uses_mock(self):
        """When not configured, returns mock data"""
        with patch.dict(os.environ, {}, clear=True):
            connector = RedditConnector()
            connector._enabled = True
            connector.client_id = None
            connector.client_secret = None
            connector.reddit = None
            
            result = await connector.fetch_with_fallback("test query")
            
            assert result.status == ConnectorStatus.NOT_CONFIGURED
            assert "not configured" in result.message.lower()
            assert isinstance(result.data, list)


# Real API tests
@pytest.mark.skipif(
    not (os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
    reason="Reddit credentials not set"
)
class TestRedditRealAPI:
    """Tests against real Reddit API"""
    
    @pytest.mark.asyncio
    async def test_real_api_search(self):
        """Test real API search"""
        connector = RedditConnector()
        
        if not connector.is_configured():
            pytest.skip("Reddit not configured")
        
        result = await connector.fetch("python programming", limit=5)
        
        print(f"\nReal API Result: {result.message}")
        print(f"Items: {result.items_count}")
        
        if result.status == ConnectorStatus.SUCCESS:
            assert result.items_count > 0
            if result.data:
                print(f"First post: {result.data[0]['title'][:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
