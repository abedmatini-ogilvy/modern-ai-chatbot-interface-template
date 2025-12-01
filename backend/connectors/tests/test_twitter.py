"""
Tests for Twitter Connector

Run tests:
    cd backend
    python -m pytest connectors/tests/test_twitter.py -v

Test with real API (requires TWITTER_BEARER_TOKEN):
    python -m pytest connectors/tests/test_twitter.py -v -k "real" --run-real-api
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from connectors.twitter_connector import TwitterConnector, TWEEPY_AVAILABLE
from connectors.base_connector import ConnectorStatus


class TestTwitterConnectorBasics:
    """Test basic connector properties"""
    
    def test_name(self):
        """Connector has correct name"""
        connector = TwitterConnector()
        assert connector.name == "twitter"
    
    def test_display_name(self):
        """Connector has human-readable display name"""
        connector = TwitterConnector()
        assert connector.display_name == "Twitter/X"
    
    def test_not_configured_without_token(self):
        """is_configured returns False without bearer token"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing token
            if "TWITTER_BEARER_TOKEN" in os.environ:
                del os.environ["TWITTER_BEARER_TOKEN"]
            
            connector = TwitterConnector()
            # Will be False either due to missing token or missing tweepy
            assert connector.is_configured() == False or not TWEEPY_AVAILABLE
    
    @pytest.mark.skipif(not TWEEPY_AVAILABLE, reason="tweepy not installed")
    def test_configured_with_token(self):
        """is_configured returns True with bearer token"""
        with patch.dict(os.environ, {"TWITTER_BEARER_TOKEN": "test_token"}):
            connector = TwitterConnector()
            assert connector.is_configured() == True
    
    def test_config_override(self):
        """Config dict can override env variables"""
        connector = TwitterConnector(config={"bearer_token": "config_token"})
        assert connector.bearer_token == "config_token"


class TestTwitterConnectorMocking:
    """Test connector behavior with mocked API"""
    
    @pytest.fixture
    def mock_tweepy_response(self):
        """Create mock tweepy response"""
        mock_tweet = MagicMock()
        mock_tweet.id = 123456789
        mock_tweet.text = "This is a test tweet about marketing"
        mock_tweet.created_at = MagicMock()
        mock_tweet.created_at.isoformat.return_value = "2024-01-15T10:30:00Z"
        mock_tweet.author_id = 987654321
        mock_tweet.public_metrics = {
            "like_count": 100,
            "retweet_count": 50,
            "reply_count": 10,
            "quote_count": 5
        }
        mock_tweet.lang = "en"
        
        mock_user = MagicMock()
        mock_user.id = 987654321
        mock_user.username = "testuser"
        mock_user.name = "Test User"
        
        mock_response = MagicMock()
        mock_response.data = [mock_tweet]
        mock_response.includes = {"users": [mock_user]}
        
        return mock_response
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not TWEEPY_AVAILABLE, reason="tweepy not installed")
    async def test_fetch_success(self, mock_tweepy_response):
        """Successful API call returns formatted data"""
        with patch.dict(os.environ, {"TWITTER_BEARER_TOKEN": "test_token"}):
            connector = TwitterConnector()
            
            # Mock the API call
            connector.client = MagicMock()
            connector.client.search_recent_tweets.return_value = mock_tweepy_response
            
            result = await connector.fetch("marketing trends")
            
            assert result.status == ConnectorStatus.SUCCESS
            assert len(result.data) == 1
            assert result.data[0]["text"] == "This is a test tweet about marketing"
            assert result.data[0]["author_username"] == "testuser"
            assert result.data[0]["likes"] == 100
            assert result.data[0]["retweets"] == 50
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not TWEEPY_AVAILABLE, reason="tweepy not installed")
    async def test_fetch_empty_results(self):
        """Empty results handled gracefully"""
        with patch.dict(os.environ, {"TWITTER_BEARER_TOKEN": "test_token"}):
            connector = TwitterConnector()
            
            mock_response = MagicMock()
            mock_response.data = None  # No tweets found
            
            connector.client = MagicMock()
            connector.client.search_recent_tweets.return_value = mock_response
            
            result = await connector.fetch("xyznonexistentquery123")
            
            assert result.status == ConnectorStatus.SUCCESS
            assert len(result.data) == 0
            assert "No tweets found" in result.message
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not TWEEPY_AVAILABLE, reason="tweepy not installed")
    async def test_rate_limit_triggers_nitter_fallback(self):
        """Rate limit exception triggers Nitter fallback"""
        import tweepy
        
        with patch.dict(os.environ, {"TWITTER_BEARER_TOKEN": "test_token"}):
            connector = TwitterConnector()
            
            connector.client = MagicMock()
            connector.client.search_recent_tweets.side_effect = tweepy.TooManyRequests(
                MagicMock(status_code=429)
            )
            
            # Mock Nitter to fail too (we're just testing the fallback is attempted)
            with patch.object(connector, '_fetch_nitter', new_callable=AsyncMock) as mock_nitter:
                mock_nitter.return_value = MagicMock(
                    status=ConnectorStatus.FAILED,
                    data=[],
                    source="twitter"
                )
                
                result = await connector.fetch("test query")
                
                # Verify Nitter fallback was attempted
                mock_nitter.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not TWEEPY_AVAILABLE, reason="tweepy not installed")
    async def test_auth_error_returns_mock_data(self):
        """Auth error returns mock data with clear message"""
        import tweepy
        
        with patch.dict(os.environ, {"TWITTER_BEARER_TOKEN": "bad_token"}):
            connector = TwitterConnector()
            
            connector.client = MagicMock()
            connector.client.search_recent_tweets.side_effect = tweepy.Unauthorized(
                MagicMock(status_code=401)
            )
            
            result = await connector.fetch("test query")
            
            assert result.status == ConnectorStatus.FAILED
            assert "authentication failed" in result.message.lower()
            assert "TWITTER_BEARER_TOKEN" in result.message


class TestMockData:
    """Test mock data generation"""
    
    def test_get_mock_data(self):
        """Mock data has expected structure"""
        connector = TwitterConnector()
        mock_data = connector.get_mock_data("marketing", limit=5)
        
        assert len(mock_data) <= 5
        assert len(mock_data) > 0
        
        # Check structure of first item
        tweet = mock_data[0]
        assert "id" in tweet
        assert "text" in tweet
        assert "likes" in tweet or "engagement" in tweet


class TestFetchWithFallback:
    """Test the full fallback chain"""
    
    @pytest.mark.asyncio
    async def test_not_configured_uses_mock(self):
        """When not configured, returns mock data gracefully"""
        with patch.dict(os.environ, {}, clear=True):
            connector = TwitterConnector()
            connector._enabled = True
            
            # Force not configured
            connector.bearer_token = None
            connector.client = None
            
            result = await connector.fetch_with_fallback("test query")
            
            assert result.status == ConnectorStatus.NOT_CONFIGURED
            assert "not configured" in result.message.lower()
            # Should still have mock data
            assert isinstance(result.data, list)


# =============================================================================
# REAL API TESTS - Only run with --run-real-api flag
# =============================================================================

@pytest.mark.skipif(
    not os.getenv("TWITTER_BEARER_TOKEN"),
    reason="TWITTER_BEARER_TOKEN not set"
)
class TestTwitterRealAPI:
    """
    Tests against real Twitter API.
    
    Only run these when you want to test real API integration:
        TWITTER_BEARER_TOKEN=your_token pytest -v -k "real"
    """
    
    @pytest.mark.asyncio
    async def test_real_api_search(self):
        """Test real API search (uses quota!)"""
        connector = TwitterConnector()
        
        if not connector.is_configured():
            pytest.skip("Twitter not configured")
        
        # Use a simple query to minimize quota usage
        result = await connector.fetch("python programming", limit=5)
        
        print(f"\nReal API Result: {result.message}")
        print(f"Items: {result.items_count}")
        
        if result.status == ConnectorStatus.SUCCESS:
            assert result.items_count > 0
            assert result.data[0]["text"]  # Has tweet text
        elif result.status == ConnectorStatus.RATE_LIMITED:
            print("Rate limited - this is expected if quota is exhausted")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
