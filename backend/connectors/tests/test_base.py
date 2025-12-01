"""
Tests for BaseConnector and core connector infrastructure.

These tests verify:
1. Abstract class cannot be instantiated
2. ConnectorResult works correctly
3. ConnectorStatus enum values
4. Subclasses must implement required methods
"""

import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from connectors.base_connector import (
    BaseConnector, 
    ConnectorResult, 
    ConnectorStatus
)


class TestConnectorStatus:
    """Test ConnectorStatus enum"""
    
    def test_status_values(self):
        """Verify all status codes exist and have string values"""
        assert ConnectorStatus.SUCCESS.value == "success"
        assert ConnectorStatus.PARTIAL.value == "partial"
        assert ConnectorStatus.FAILED.value == "failed"
        assert ConnectorStatus.RATE_LIMITED.value == "rate_limited"
        assert ConnectorStatus.DISABLED.value == "disabled"
        assert ConnectorStatus.NOT_CONFIGURED.value == "not_configured"
    
    def test_status_comparison(self):
        """Verify enum comparison works"""
        status = ConnectorStatus.SUCCESS
        assert status == ConnectorStatus.SUCCESS
        assert status != ConnectorStatus.FAILED


class TestConnectorResult:
    """Test ConnectorResult dataclass"""
    
    def test_create_result(self):
        """Can create a result with required fields"""
        result = ConnectorResult(
            status=ConnectorStatus.SUCCESS,
            data=[{"id": 1, "text": "test"}],
            source="test",
            message="Test message",
            items_count=1
        )
        
        assert result.status == ConnectorStatus.SUCCESS
        assert len(result.data) == 1
        assert result.source == "test"
        assert result.items_count == 1
        assert result.cached == False  # Default
        assert result.error_detail is None  # Default
    
    def test_is_success_property(self):
        """is_success returns True only for SUCCESS status"""
        success = ConnectorResult(
            status=ConnectorStatus.SUCCESS,
            data=[],
            source="test",
            message="OK",
            items_count=0
        )
        assert success.is_success == True
        
        failed = ConnectorResult(
            status=ConnectorStatus.FAILED,
            data=[],
            source="test",
            message="Error",
            items_count=0
        )
        assert failed.is_success == False
    
    def test_has_data_property(self):
        """has_data returns True when data list is not empty"""
        with_data = ConnectorResult(
            status=ConnectorStatus.SUCCESS,
            data=[{"item": 1}],
            source="test",
            message="OK",
            items_count=1
        )
        assert with_data.has_data == True
        
        without_data = ConnectorResult(
            status=ConnectorStatus.SUCCESS,
            data=[],
            source="test",
            message="OK",
            items_count=0
        )
        assert without_data.has_data == False
    
    def test_to_dict(self):
        """to_dict returns serializable dictionary"""
        result = ConnectorResult(
            status=ConnectorStatus.SUCCESS,
            data=[{"id": 1}],
            source="test",
            message="Test",
            items_count=1
        )
        
        d = result.to_dict()
        
        assert d["status"] == "success"  # String, not enum
        assert d["data"] == [{"id": 1}]
        assert d["source"] == "test"
        assert "timestamp" in d  # Auto-generated


class TestBaseConnector:
    """Test BaseConnector abstract class"""
    
    def test_cannot_instantiate_directly(self):
        """BaseConnector is abstract - cannot be instantiated"""
        with pytest.raises(TypeError) as exc_info:
            BaseConnector()
        
        # Error should mention abstract methods
        assert "abstract" in str(exc_info.value).lower()
    
    def test_subclass_must_implement_abstract_methods(self):
        """Subclass without implementations raises TypeError"""
        
        class IncompleteConnector(BaseConnector):
            pass  # Missing all required implementations
        
        with pytest.raises(TypeError):
            IncompleteConnector()
    
    def test_complete_subclass_works(self):
        """Properly implemented subclass can be instantiated"""
        
        class TestConnector(BaseConnector):
            @property
            def name(self) -> str:
                return "test"
            
            @property
            def display_name(self) -> str:
                return "Test Connector"
            
            async def fetch(self, query: str, **kwargs):
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=[{"query": query}],
                    source=self.name,
                    message="OK",
                    items_count=1
                )
            
            def is_configured(self) -> bool:
                return True
        
        connector = TestConnector()
        assert connector.name == "test"
        assert connector.display_name == "Test Connector"
        assert connector.is_configured() == True


class TestConnectorBehavior:
    """Test connector behaviors with a concrete implementation"""
    
    @pytest.fixture
    def mock_connector(self):
        """Create a test connector for behavior tests"""
        
        class MockConnector(BaseConnector):
            def __init__(self, config=None):
                super().__init__(config)
                self._configured = True
                self._should_fail = False
            
            @property
            def name(self) -> str:
                return "mock"
            
            @property
            def display_name(self) -> str:
                return "Mock Connector"
            
            async def fetch(self, query: str, **kwargs):
                if self._should_fail:
                    raise Exception("API Error")
                return ConnectorResult(
                    status=ConnectorStatus.SUCCESS,
                    data=[{"query": query, "result": "real data"}],
                    source=self.name,
                    message="Retrieved data",
                    items_count=1
                )
            
            def is_configured(self) -> bool:
                return self._configured
            
            def get_mock_data(self, query: str, **kwargs):
                return [{"query": query, "result": "mock data"}]
        
        return MockConnector()
    
    @pytest.mark.asyncio
    async def test_fetch_with_fallback_success(self, mock_connector):
        """When configured and working, returns real data"""
        result = await mock_connector.fetch_with_fallback("test query")
        
        assert result.status == ConnectorStatus.SUCCESS
        assert result.data[0]["result"] == "real data"
        assert result.cached == False
    
    @pytest.mark.asyncio
    async def test_fetch_with_fallback_not_configured(self, mock_connector):
        """When not configured, returns mock data"""
        mock_connector._configured = False
        
        result = await mock_connector.fetch_with_fallback("test query")
        
        assert result.status == ConnectorStatus.NOT_CONFIGURED
        assert result.data[0]["result"] == "mock data"
        assert "not configured" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_with_fallback_on_error(self, mock_connector):
        """When API fails, returns mock data"""
        mock_connector._should_fail = True
        
        result = await mock_connector.fetch_with_fallback("test query")
        
        assert result.status == ConnectorStatus.FAILED
        assert result.data[0]["result"] == "mock data"
        assert result.error_detail is not None
    
    @pytest.mark.asyncio
    async def test_disabled_connector(self, mock_connector):
        """Disabled connector returns disabled status"""
        mock_connector.disable()
        
        result = await mock_connector.fetch_with_fallback("test query")
        
        assert result.status == ConnectorStatus.DISABLED
        assert len(result.data) == 0
    
    @pytest.mark.asyncio
    async def test_empty_query_rejected(self, mock_connector):
        """Empty query is rejected"""
        result = await mock_connector.fetch_with_fallback("")
        
        assert result.status == ConnectorStatus.FAILED
        assert "empty" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_caching(self, mock_connector):
        """Second call returns cached result"""
        # First call
        result1 = await mock_connector.fetch_with_fallback("test query")
        assert result1.cached == False
        
        # Second call - should be cached
        result2 = await mock_connector.fetch_with_fallback("test query")
        assert result2.cached == True
        assert "(cached)" in result2.message
    
    def test_get_status(self, mock_connector):
        """get_status returns connector info"""
        status = mock_connector.get_status()
        
        assert status["name"] == "mock"
        assert status["display_name"] == "Mock Connector"
        assert status["enabled"] == True
        assert status["configured"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
