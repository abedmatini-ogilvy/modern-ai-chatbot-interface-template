"""
Modular API Connectors Package

This package provides a unified interface for fetching data from various APIs.
Each connector follows the same pattern:
    1. Inherits from BaseConnector
    2. Implements fetch() method
    3. Returns standardized ConnectorResult
    4. Falls back to mock data on failure

Usage:
    from connectors import get_connector, get_all_connectors
    
    # Get a specific connector
    twitter = get_connector("twitter")
    result = await twitter.fetch_with_fallback("marketing trends")
    
    # Get all connectors
    connectors = get_all_connectors()
    for name, connector in connectors.items():
        result = await connector.fetch_with_fallback(query)
"""

from typing import Dict, Type

# Import base classes first
from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus

# Import connectors (they auto-register)
from .twitter_connector import TwitterConnector
from .reddit_connector import RedditConnector
from .google_trends_connector import GoogleTrendsConnector
from .web_search_connector import WebSearchConnector
from .tiktok_connector import TikTokConnector
from .llm_connector import LLMConnector, LLMProvider, get_llm_connector

# Connector registry - will be populated as we implement each connector
# For now, we'll have placeholders that will be replaced
CONNECTORS: Dict[str, Type[BaseConnector]] = {
    "twitter": TwitterConnector,
    "reddit": RedditConnector,
    "google_trends": GoogleTrendsConnector,
    "web_search": WebSearchConnector,
    "tiktok": TikTokConnector,
    "llm": LLMConnector,
}

def get_connector(name: str, config: Dict = None) -> BaseConnector:
    """
    Factory function to get a connector by name.
    
    Args:
        name: Connector name ('twitter', 'reddit', etc.)
        config: Optional configuration dict
        
    Returns:
        Connector instance
        
    Raises:
        ValueError: If connector name is unknown
    """
    if name not in CONNECTORS:
        available = ", ".join(CONNECTORS.keys()) or "none yet"
        raise ValueError(f"Unknown connector: {name}. Available: {available}")
    return CONNECTORS[name](config)


def get_all_connectors(config: Dict = None) -> Dict[str, BaseConnector]:
    """
    Get instances of all registered connectors.
    
    Args:
        config: Optional configuration dict shared by all connectors
        
    Returns:
        Dict mapping connector names to instances
    """
    return {name: cls(config) for name, cls in CONNECTORS.items()}


def register_connector(name: str, connector_class: Type[BaseConnector]):
    """
    Register a new connector in the registry.
    
    Args:
        name: Unique name for the connector
        connector_class: The connector class (not instance)
    """
    CONNECTORS[name] = connector_class


def get_configured_connectors(config: Dict = None) -> Dict[str, BaseConnector]:
    """
    Get only connectors that have valid API credentials configured.
    
    Returns:
        Dict of configured connector instances
    """
    all_connectors = get_all_connectors(config)
    return {
        name: connector 
        for name, connector in all_connectors.items() 
        if connector.is_configured()
    }


# Export public API
__all__ = [
    # Base classes
    "BaseConnector",
    "ConnectorResult",
    "ConnectorStatus",
    # Connectors
    "TwitterConnector",
    "RedditConnector",
    "GoogleTrendsConnector",
    "WebSearchConnector",
    "TikTokConnector",
    "LLMConnector",
    "LLMProvider",
    # Utilities
    "get_llm_connector",
    # Factory functions
    "get_connector",
    "get_all_connectors",
    "get_configured_connectors",
    "register_connector",
    # Registry
    "CONNECTORS",
]
