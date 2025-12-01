"""
Tests for Google Trends Connector

Run tests:
    cd backend
    python -m pytest connectors/tests/test_google_trends.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from connectors.google_trends_connector import GoogleTrendsConnector, PYTRENDS_AVAILABLE
from connectors.base_connector import ConnectorStatus


class TestGoogleTrendsBasics:
    """Test basic connector properties"""
    
    def test_name(self):
        connector = GoogleTrendsConnector()
        assert connector.name == "google_trends"
    
    def test_display_name(self):
        connector = GoogleTrendsConnector()
        assert connector.display_name == "Google Trends"
    
    @pytest.mark.skipif(not PYTRENDS_AVAILABLE, reason="pytrends not installed")
    def test_always_configured(self):
        """Google Trends doesn't need API keys"""
        connector = GoogleTrendsConnector()
        assert connector.is_configured() == True
    
    def test_config_options(self):
        """Config options are applied"""
        connector = GoogleTrendsConnector(config={
            "hl": "de-DE",
            "geo": "DE",
            "tz": 60
        })
        assert connector.hl == "de-DE"
        assert connector.geo == "DE"
        assert connector.tz == 60


class TestKeywordParsing:
    """Test keyword parsing logic"""
    
    def test_comma_separated(self):
        connector = GoogleTrendsConnector()
        keywords = connector._parse_keywords("marketing, social media, TikTok")
        
        assert len(keywords) == 3
        assert "marketing" in keywords
        assert "social media" in keywords
        assert "TikTok" in keywords
    
    def test_single_keyword(self):
        connector = GoogleTrendsConnector()
        keywords = connector._parse_keywords("marketing trends")
        
        assert len(keywords) == 1
        assert keywords[0] == "marketing trends"
    
    def test_max_five_keywords(self):
        """Google Trends only accepts 5 keywords max"""
        connector = GoogleTrendsConnector()
        keywords = connector._parse_keywords("a, b, c, d, e, f, g, h")
        
        assert len(keywords) == 5
    
    def test_empty_keywords_filtered(self):
        connector = GoogleTrendsConnector()
        keywords = connector._parse_keywords("marketing, , trends, ")
        
        assert len(keywords) == 2
        assert "" not in keywords


class TestGoogleTrendsMocking:
    """Test connector with mocked pytrends"""
    
    @pytest.fixture
    def mock_interest_over_time(self):
        """Create mock interest over time DataFrame"""
        return pd.DataFrame({
            'marketing': [50, 60, 75, 65],
            'social media': [40, 55, 70, 60],
            'isPartial': [False, False, False, True]
        }, index=pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']))
    
    @pytest.fixture
    def mock_related_queries(self):
        """Create mock related queries"""
        return {
            'marketing': {
                'top': pd.DataFrame({
                    'query': ['marketing strategy', 'digital marketing'],
                    'value': [100, 85]
                }),
                'rising': pd.DataFrame({
                    'query': ['marketing AI', 'marketing 2024'],
                    'value': ['Breakout', '+200%']
                })
            }
        }
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PYTRENDS_AVAILABLE, reason="pytrends not installed")
    async def test_fetch_success(self, mock_interest_over_time, mock_related_queries):
        """Successful fetch returns trend data"""
        connector = GoogleTrendsConnector()
        
        with patch.object(connector, '_get_client') as mock_client:
            mock_pytrends = MagicMock()
            mock_pytrends.interest_over_time.return_value = mock_interest_over_time
            mock_pytrends.related_queries.return_value = mock_related_queries
            mock_pytrends.interest_by_region.return_value = pd.DataFrame()
            mock_client.return_value = mock_pytrends
            
            result = await connector.fetch("marketing")
            
            assert result.status == ConnectorStatus.SUCCESS
            assert len(result.data) == 1
            assert "interest_over_time" in result.data[0]
            assert "related_queries" in result.data[0]
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PYTRENDS_AVAILABLE, reason="pytrends not installed")
    async def test_fetch_multiple_keywords(self, mock_interest_over_time):
        """Can fetch data for multiple keywords"""
        connector = GoogleTrendsConnector()
        
        with patch.object(connector, '_get_client') as mock_client:
            mock_pytrends = MagicMock()
            mock_pytrends.interest_over_time.return_value = mock_interest_over_time
            mock_pytrends.related_queries.return_value = {}
            mock_pytrends.interest_by_region.return_value = pd.DataFrame()
            mock_client.return_value = mock_pytrends
            
            result = await connector.fetch("marketing, social media")
            
            assert result.status == ConnectorStatus.SUCCESS
            data = result.data[0]
            assert len(data["keywords"]) == 2
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not PYTRENDS_AVAILABLE, reason="pytrends not installed")
    async def test_rate_limit_handling(self):
        """Rate limit returns appropriate status"""
        connector = GoogleTrendsConnector()
        
        with patch.object(connector, '_get_client') as mock_client:
            mock_pytrends = MagicMock()
            mock_pytrends.interest_over_time.side_effect = Exception("429 Too Many Requests")
            mock_client.return_value = mock_pytrends
            
            result = await connector.fetch("test")
            
            assert result.status == ConnectorStatus.RATE_LIMITED
            assert "rate limited" in result.message.lower()


class TestMockData:
    """Test mock data generation"""
    
    def test_get_mock_data(self):
        """Mock data has expected structure"""
        connector = GoogleTrendsConnector()
        mock_data = connector.get_mock_data("marketing")
        
        assert len(mock_data) == 1
        data = mock_data[0]
        
        assert "keywords" in data
        assert "interest_over_time" in data
        assert "related_queries" in data


class TestFetchWithFallback:
    """Test fallback behavior"""
    
    @pytest.mark.asyncio
    async def test_pytrends_not_installed(self):
        """When pytrends not installed, uses mock data"""
        connector = GoogleTrendsConnector()
        
        # Simulate pytrends not available
        with patch('connectors.google_trends_connector.PYTRENDS_AVAILABLE', False):
            connector_new = GoogleTrendsConnector()
            assert connector_new.is_configured() == False


# Real API tests (use sparingly to avoid rate limits)
@pytest.mark.skipif(not PYTRENDS_AVAILABLE, reason="pytrends not installed")
class TestGoogleTrendsRealAPI:
    """
    Tests against real Google Trends.
    
    WARNING: Use sparingly! Google may rate limit.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Skip by default to avoid rate limits")
    async def test_real_api_search(self):
        """Test real Google Trends search"""
        connector = GoogleTrendsConnector()
        
        result = await connector.fetch("Python programming", timeframe="today 1-m")
        
        print(f"\nReal API Result: {result.message}")
        
        if result.status == ConnectorStatus.SUCCESS:
            data = result.data[0]
            print(f"Keywords: {data['keywords']}")
            if data.get('interest_over_time', {}).get('summary'):
                print(f"Summary: {data['interest_over_time']['summary']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
