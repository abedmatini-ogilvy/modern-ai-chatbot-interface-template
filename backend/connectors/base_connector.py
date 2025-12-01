"""
Base Connector - Abstract base class for all API connectors

This module defines the contract that all connectors must follow.
Key concepts:

1. ABSTRACT CLASS: Cannot be instantiated directly, must be subclassed
2. ABSTRACT METHODS: Subclasses MUST implement these (fetch, is_configured, etc.)
3. TEMPLATE METHOD: fetch_with_fallback() provides common logic, calls abstract methods
4. DATACLASS: ConnectorResult is a simple container for results

Design Pattern: Template Method Pattern
- Base class defines the algorithm structure (fetch_with_fallback)
- Subclasses provide specific implementations (fetch)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import os

# Load .env file at module import time
# This ensures environment variables are available for all connectors
from dotenv import load_dotenv
load_dotenv()


class ConnectorStatus(Enum):
    """
    Status codes for connector results.
    
    Using Enum instead of strings provides:
    - Type safety (can't misspell)
    - IDE autocomplete
    - Easy comparison (status == ConnectorStatus.SUCCESS)
    """
    SUCCESS = "success"           # Got real data from API
    PARTIAL = "partial"           # Got some data or using mock
    FAILED = "failed"             # API call failed
    RATE_LIMITED = "rate_limited" # Hit API rate limit
    DISABLED = "disabled"         # Connector disabled by config
    NOT_CONFIGURED = "not_configured"  # Missing API credentials


@dataclass
class ConnectorResult:
    """
    Standardized result format for all connectors.
    
    Using @dataclass decorator auto-generates:
    - __init__() with all fields as parameters
    - __repr__() for debugging
    - __eq__() for comparison
    
    This ensures every connector returns the same structure,
    making it easy to process results uniformly.
    """
    status: ConnectorStatus          # What happened
    data: List[Dict[str, Any]]       # The actual data (list of items)
    source: str                       # Connector name (e.g., "twitter")
    message: str                      # Human-readable status message
    items_count: int                  # Number of items returned
    cached: bool = False              # Was this from cache?
    error_detail: Optional[str] = None  # Technical error info for debugging
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # When fetched
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status.value,
            "data": self.data,
            "source": self.source,
            "message": self.message,
            "items_count": self.items_count,
            "cached": self.cached,
            "error_detail": self.error_detail,
            "timestamp": self.timestamp.isoformat()
        }
    
    @property
    def is_success(self) -> bool:
        """Quick check if we got real data"""
        return self.status == ConnectorStatus.SUCCESS
    
    @property
    def has_data(self) -> bool:
        """Check if we have any data (even mock/partial)"""
        return len(self.data) > 0


class BaseConnector(ABC):
    """
    Abstract base class that all connectors must inherit from.
    
    ABC = Abstract Base Class
    - Cannot be instantiated directly: BaseConnector() raises error
    - Subclasses MUST implement @abstractmethod decorated methods
    - Provides common functionality (logging, fallback logic)
    
    Why use this pattern?
    1. Consistency: All connectors have same interface
    2. Polymorphism: Can treat all connectors the same way
    3. Reusability: Common code lives here, not duplicated
    4. Testing: Can mock any connector with same interface
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize base connector.
        
        Args:
            config: Optional configuration dictionary
                   Can override environment variables
        """
        self.config = config or {}
        # Each connector gets its own logger with its class name
        self.logger = logging.getLogger(self.__class__.__name__)
        self._enabled = True
        self._cache: Dict[str, ConnectorResult] = {}
    
    # ==========================================================================
    # ABSTRACT PROPERTIES - Subclasses MUST define these
    # ==========================================================================
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this connector (e.g., 'twitter', 'reddit').
        Used as key in registries and results.
        
        Example:
            @property
            def name(self) -> str:
                return "twitter"
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable name for UI display (e.g., 'Twitter/X', 'Reddit').
        
        Example:
            @property
            def display_name(self) -> str:
                return "Twitter/X"
        """
        pass
    
    # ==========================================================================
    # ABSTRACT METHODS - Subclasses MUST implement these
    # ==========================================================================
    
    @abstractmethod
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch data from the real API.
        
        This is where the actual API call happens.
        Should NOT handle fallbacks - that's done by fetch_with_fallback().
        
        Args:
            query: Search query string
            **kwargs: Additional parameters like:
                     - limit: Max items to return
                     - date_from: Start date
                     - date_to: End date
                     
        Returns:
            ConnectorResult with data or error status
            
        Raises:
            Should NOT raise exceptions - catch and return FAILED status
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if required API credentials are available.
        
        Returns True if the connector has all required credentials
        to make real API calls.
        
        Example:
            def is_configured(self) -> bool:
                return bool(os.getenv("TWITTER_BEARER_TOKEN"))
        """
        pass
    
    # ==========================================================================
    # OPTIONAL OVERRIDE - Subclasses CAN override these
    # ==========================================================================
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return mock/sample data as fallback.
        
        Override this to provide realistic sample data when API fails.
        Default returns empty list.
        
        Args:
            query: The search query (can be used to customize mock data)
            
        Returns:
            List of mock data items in same format as real API
        """
        return []
    
    def validate_query(self, query: str) -> Optional[str]:
        """
        Validate and potentially clean the search query.
        
        Override to add query validation/sanitization.
        
        Returns:
            Error message if invalid, None if valid
        """
        if not query or not query.strip():
            return "Query cannot be empty"
        return None
    
    # ==========================================================================
    # CORE METHODS - Usually don't need to override
    # ==========================================================================
    
    async def fetch_with_fallback(self, query: str, **kwargs) -> ConnectorResult:
        """
        Fetch data with automatic fallback to mock data.
        
        This is the MAIN method to call - it handles:
        1. Check if connector is enabled
        2. Check if credentials are configured
        3. Try real API call
        4. Fall back to mock data on any failure
        5. Log everything for debugging
        
        TEMPLATE METHOD PATTERN:
        - This method defines the algorithm
        - Calls abstract methods (fetch, is_configured) that subclasses provide
        
        Args:
            query: Search query string
            **kwargs: Passed to fetch()
            
        Returns:
            ConnectorResult - always returns something, never raises
        """
        # 1. Check if disabled
        if not self._enabled:
            self.logger.info(f"{self.name} connector is disabled")
            return ConnectorResult(
                status=ConnectorStatus.DISABLED,
                data=[],
                source=self.name,
                message=f"{self.display_name} is disabled",
                items_count=0
            )
        
        # 2. Validate query
        validation_error = self.validate_query(query)
        if validation_error:
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message=validation_error,
                items_count=0,
                error_detail="Query validation failed"
            )
        
        # 3. Check cache (if implemented)
        cache_key = self._make_cache_key(query, **kwargs)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            self.logger.info(f"{self.name}: Returning cached result")
            return ConnectorResult(
                status=cached.status,
                data=cached.data,
                source=self.name,
                message=f"{cached.message} (cached)",
                items_count=cached.items_count,
                cached=True
            )
        
        # 4. Check if API credentials are configured
        if not self.is_configured():
            self.logger.warning(f"{self.name} not configured, using mock data")
            mock_data = self.get_mock_data(query, **kwargs)
            return ConnectorResult(
                status=ConnectorStatus.NOT_CONFIGURED,
                data=mock_data,
                source=self.name,
                message=f"{self.display_name} not configured - using sample data",
                items_count=len(mock_data)
            )
        
        # 5. Try the real API call
        try:
            self.logger.info(f"{self.name}: Fetching real data for '{query}'")
            result = await self.fetch(query, **kwargs)
            
            # Cache successful results
            if result.is_success:
                self._cache[cache_key] = result
                
            return result
            
        except Exception as e:
            # 6. On ANY error, fall back to mock data
            self.logger.error(f"{self.name} fetch failed: {type(e).__name__}: {e}")
            mock_data = self.get_mock_data(query, **kwargs)
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=mock_data,
                source=self.name,
                message=f"{self.display_name} unavailable - using sample data",
                items_count=len(mock_data),
                error_detail=f"{type(e).__name__}: {str(e)}"
            )
    
    def _make_cache_key(self, query: str, **kwargs) -> str:
        """Generate cache key from query and parameters"""
        # Simple cache key - can be overridden for more complex caching
        params = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{self.name}:{query}:{params}"
    
    def clear_cache(self):
        """Clear the connector's cache"""
        self._cache.clear()
        self.logger.info(f"{self.name}: Cache cleared")
    
    def enable(self):
        """Enable the connector"""
        self._enabled = True
        self.logger.info(f"{self.name}: Enabled")
    
    def disable(self):
        """Disable the connector"""
        self._enabled = False
        self.logger.info(f"{self.name}: Disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connector status for debugging/monitoring"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "enabled": self._enabled,
            "configured": self.is_configured(),
            "cache_size": len(self._cache)
        }
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        status = "✓" if self.is_configured() else "✗"
        enabled = "enabled" if self._enabled else "disabled"
        return f"<{self.__class__.__name__} [{status}] {enabled}>"
