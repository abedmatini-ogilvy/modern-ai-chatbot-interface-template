"""
LLM Connector - Multi-Provider AI Analysis

This connector handles AI-powered analysis using multiple LLM providers.

Supported Providers:
1. Google Gemini (Primary) - Free tier: 60 req/min, 1M tokens/day
2. Azure OpenAI - Pay-as-you-go
3. OpenAI (Direct) - Pay-as-you-go

Architecture: Strategy Pattern
- LLMConnector is the main interface
- Each provider is a separate strategy
- Easy to add new providers without changing existing code

Key Design Decisions:
1. Start with Gemini (generous free tier)
2. Support switching providers via frontend
3. Graceful fallback between providers
4. Consistent analysis output format

Environment Variables:
- DEFAULT_LLM_PROVIDER: "gemini", "azure", or "openai"
- GOOGLE_AI_API_KEY: Gemini API key
- AZURE_OPENAI_API_KEY: Azure key
- AZURE_OPENAI_ENDPOINT: Azure endpoint
- AZURE_OPENAI_DEPLOYMENT_NAME: Model deployment name
- OPENAI_API_KEY: Direct OpenAI key (optional)
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime, timezone
import logging
from abc import ABC, abstractmethod

from .base_connector import BaseConnector, ConnectorResult, ConnectorStatus


class LLMProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    AZURE_OPENAI = "azure"
    OPENAI = "openai"
    MOCK = "mock"


# =============================================================================
# Provider Strategies (Strategy Pattern)
# =============================================================================

class BaseLLMProvider(ABC):
    """
    Abstract base for LLM providers.
    
    Strategy Pattern: Each provider implements same interface.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider.
    
    Free tier: 60 requests/minute, 1M tokens/day
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
        self._client = None
        self.logger = logging.getLogger("GeminiProvider")
    
    @property
    def name(self) -> str:
        return "gemini"
    
    def is_configured(self) -> bool:
        try:
            import google.generativeai
            return bool(self.api_key)
        except ImportError:
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        
        # Gemini is sync, run in executor
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )
        
        return response.text


class AzureOpenAIProvider(BaseLLMProvider):
    """
    Azure OpenAI provider.
    
    Pay-as-you-go: ~$0.01-0.03 per 1K tokens
    """
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.logger = logging.getLogger("AzureOpenAIProvider")
    
    @property
    def name(self) -> str:
        return "azure"
    
    def is_configured(self) -> bool:
        try:
            from openai import AzureOpenAI
            return bool(self.api_key and self.endpoint)
        except ImportError:
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a marketing research analyst providing data-driven insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7)
            )
        )
        
        return response.choices[0].message.content


class OpenAIProvider(BaseLLMProvider):
    """
    Direct OpenAI provider (non-Azure).
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.logger = logging.getLogger("OpenAIProvider")
    
    @property
    def name(self) -> str:
        return "openai"
    
    def is_configured(self) -> bool:
        try:
            from openai import OpenAI
            return bool(self.api_key)
        except ImportError:
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_key)
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing research analyst providing data-driven insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7)
            )
        )
        
        return response.choices[0].message.content


class MockProvider(BaseLLMProvider):
    """
    Mock provider for testing without API keys.
    """
    
    @property
    def name(self) -> str:
        return "mock"
    
    def is_configured(self) -> bool:
        return True  # Always available
    
    async def generate(self, prompt: str, **kwargs) -> str:
        # Extract data summary from prompt for context-aware mock
        return self._generate_mock_analysis(prompt)
    
    def _generate_mock_analysis(self, prompt: str) -> str:
        return """
## Research Analysis Report

### Executive Summary
This analysis is based on sample data collected from multiple sources including social media platforms, search trends, and web content. The data reveals significant patterns in consumer behavior and emerging market trends.

### Key Findings

1. **Social Media Engagement**: High engagement rates observed across Twitter and Reddit communities discussing this topic.

2. **Search Interest**: Google Trends data shows sustained interest with periodic spikes correlating with industry events.

3. **Sentiment Analysis**: Overall positive sentiment with 68% favorable mentions and constructive discussions.

4. **Geographic Distribution**: Primary interest from North America (45%), Europe (30%), and emerging markets (25%).

5. **Content Themes**: Most discussions center around innovation, sustainability, and digital transformation.

### Trend Analysis

The data suggests a growing interest in this topic area, with:
- Week-over-week engagement increase of 15%
- Rising search queries for related terms
- Active community discussions on Reddit and Twitter

### Recommendations

1. **Content Strategy**: Focus on educational content that addresses common questions identified in social discussions.

2. **Timing**: Publish during peak engagement hours (9-11 AM and 2-4 PM local time).

3. **Platforms**: Prioritize Twitter and Reddit for community engagement.

4. **Keywords**: Incorporate trending related queries into content strategy.

5. **Monitoring**: Set up alerts for emerging discussions and trending topics.

---
*Note: This is a sample analysis generated without real LLM processing. Configure API keys for real AI-powered insights.*
"""


# =============================================================================
# Main LLM Connector
# =============================================================================

class LLMConnector(BaseConnector):
    """
    Multi-provider LLM connector for AI-powered analysis.
    
    Features:
    - Multiple provider support (Gemini, Azure OpenAI, OpenAI)
    - Automatic fallback between providers
    - Consistent analysis output format
    - Prompt templates for different analysis types
    
    Usage:
        connector = LLMConnector()
        
        # Analyze research data
        result = await connector.analyze(
            data=collected_research_data,
            prompt_type="analysis"
        )
        
        # Use specific provider
        result = await connector.analyze(
            data=data,
            provider="azure"
        )
        
        # Get available providers
        providers = connector.get_available_providers()
    """
    
    @property
    def name(self) -> str:
        return "llm"
    
    @property
    def display_name(self) -> str:
        return "AI Analysis"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize LLM connector with all providers.
        """
        super().__init__(config)
        
        # Default provider from env or config
        self.default_provider = (
            self.config.get("default_provider") or
            os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        )
        
        # Initialize all providers
        self._providers: Dict[str, BaseLLMProvider] = {
            "gemini": GeminiProvider(),
            "azure": AzureOpenAIProvider(),
            "openai": OpenAIProvider(),
            "mock": MockProvider()
        }
        
        # Log available providers
        available = self.get_available_providers()
        self.logger.info(f"LLM providers available: {', '.join(available)}")
    
    def is_configured(self) -> bool:
        """At least one real provider (not mock) is configured"""
        real_providers = ["gemini", "azure", "openai"]
        return any(
            self._providers[p].is_configured() 
            for p in real_providers 
            if p in self._providers
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured providers"""
        return [
            name for name, provider in self._providers.items()
            if provider.is_configured()
        ]
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider instance"""
        return self._providers.get(name)
    
    async def fetch(self, query: str, **kwargs) -> ConnectorResult:
        """
        Required by BaseConnector but not the main method.
        Use analyze() instead.
        """
        # Simple generation without structured data
        return await self.generate(query, **kwargs)
    
    async def generate(self, prompt: str, **kwargs) -> ConnectorResult:
        """
        Generate text from prompt using LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            provider: Specific provider to use (optional)
            
        Returns:
            ConnectorResult with generated text
        """
        provider_name = kwargs.get("provider", self.default_provider)
        
        # Get provider
        provider = self._providers.get(provider_name)
        if not provider or not provider.is_configured():
            # Try fallback providers
            for fallback in ["gemini", "azure", "openai", "mock"]:
                provider = self._providers.get(fallback)
                if provider and provider.is_configured():
                    provider_name = fallback
                    break
        
        try:
            text = await provider.generate(prompt, **kwargs)
            
            return ConnectorResult(
                status=ConnectorStatus.SUCCESS,
                data=[{"text": text, "provider": provider_name}],
                source=self.name,
                message=f"Generated using {provider_name}",
                items_count=1
            )
            
        except Exception as e:
            self.logger.error(f"LLM generation error ({provider_name}): {e}")
            
            # Try mock fallback
            if provider_name != "mock":
                mock = self._providers["mock"]
                text = await mock.generate(prompt)
                return ConnectorResult(
                    status=ConnectorStatus.PARTIAL,
                    data=[{"text": text, "provider": "mock"}],
                    source=self.name,
                    message="Using sample analysis (LLM unavailable)",
                    items_count=1,
                    error_detail=str(e)
                )
            
            return ConnectorResult(
                status=ConnectorStatus.FAILED,
                data=[],
                source=self.name,
                message="LLM generation failed",
                items_count=0,
                error_detail=str(e)
            )
    
    async def analyze(
        self,
        data: Dict[str, Any],
        prompt_type: str = "analysis",
        provider: Optional[str] = None,
        **kwargs
    ) -> ConnectorResult:
        """
        Analyze collected research data.
        
        This is the main method for research analysis.
        
        Args:
            data: Collected data from all connectors
                  Format: {"twitter": [...], "reddit": [...], ...}
            prompt_type: Type of analysis:
                        - "analysis": Full research analysis
                        - "summary": Brief summary
                        - "recommendations": Action items
                        - "sentiment": Sentiment analysis
            provider: Specific LLM provider (optional)
            
        Returns:
            ConnectorResult with analysis
        """
        # Build the analysis prompt
        prompt = self._build_prompt(data, prompt_type, **kwargs)
        
        # Generate analysis
        result = await self.generate(prompt, provider=provider, **kwargs)
        
        # Enhance result with analysis metadata
        if result.data:
            result.data[0]["prompt_type"] = prompt_type
            result.data[0]["sources_analyzed"] = list(data.keys())
            result.data[0]["data_points"] = sum(
                len(items) if isinstance(items, list) else 1 
                for items in data.values()
            )
        
        return result
    
    def _build_prompt(
        self, 
        data: Dict[str, Any], 
        prompt_type: str,
        **kwargs
    ) -> str:
        """
        Build analysis prompt from collected data.
        
        Prompt Engineering Best Practices:
        1. Clear role assignment
        2. Specific output format
        3. Context from data
        4. Structured requirements
        """
        # Summarize the data for the prompt
        data_summary = self._summarize_data(data)
        
        # Get research question if provided
        research_question = kwargs.get("research_question", "General market research")
        
        # Prompt templates for different analysis types
        prompts = {
            "analysis": f"""
You are a senior marketing research analyst. Analyze this research data and provide comprehensive insights.

## Research Question
{research_question}

## Collected Data
{data_summary}

## Required Output

Provide your analysis in the following format:

### Executive Summary
(2-3 sentences summarizing the key findings)

### Key Findings
(5-7 bullet points of the most important discoveries)

### Trend Analysis
(Patterns and trends observed across the data)

### Sentiment & Reception
(How the topic is being discussed - positive, negative, neutral)

### Recommendations
(5 specific, actionable recommendations for marketing strategy)

### Data Quality Notes
(Any limitations or gaps in the data)

Be specific and cite data points where relevant. Focus on actionable insights.
            """,
            
            "summary": f"""
You are a marketing analyst. Provide a brief summary of this research data.

## Research Question
{research_question}

## Data
{data_summary}

## Task
Write a 3-paragraph summary covering:
1. Main topic and context
2. Key findings and patterns
3. Overall implications

Keep it concise and focused on the most important points.
            """,
            
            "recommendations": f"""
You are a marketing strategist. Based on this research data, provide strategic recommendations.

## Research Question
{research_question}

## Data
{data_summary}

## Task
Provide 7 specific, actionable recommendations. For each:
1. State the recommendation clearly
2. Explain the rationale (tie to data)
3. Suggest implementation approach
4. Expected impact

Focus on practical, implementable strategies.
            """,
            
            "sentiment": f"""
You are a sentiment analysis expert. Analyze the sentiment in this research data.

## Research Question
{research_question}

## Data
{data_summary}

## Task
Provide sentiment analysis:
1. Overall sentiment (Positive/Negative/Neutral with percentage estimate)
2. Key positive themes (with examples)
3. Key negative themes (with examples)
4. Neutral/informational content themes
5. Sentiment by platform/source
6. Sentiment trends over time (if discernible)

Be specific and quote examples from the data.
            """
        }
        
        return prompts.get(prompt_type, prompts["analysis"])
    
    def _summarize_data(self, data: Dict[str, Any], max_items: int = 10) -> str:
        """
        Convert collected data to text for the prompt.
        
        Limits data to avoid token overflow while preserving key info.
        """
        sections = []
        
        for source, items in data.items():
            section_lines = [f"\n### {source.upper()}"]
            
            if isinstance(items, list):
                section_lines.append(f"({len(items)} items collected)")
                
                for item in items[:max_items]:
                    if isinstance(item, dict):
                        # Extract most relevant text fields
                        text = (
                            item.get("text") or 
                            item.get("title") or 
                            item.get("snippet") or 
                            item.get("description") or 
                            ""
                        )
                        # Add engagement metrics if available
                        engagement = ""
                        if "likes" in item:
                            engagement = f" [Likes: {item['likes']}]"
                        elif "score" in item:
                            engagement = f" [Score: {item['score']}]"
                        elif "views" in item:
                            engagement = f" [Views: {item['views']}]"
                        
                        if text:
                            section_lines.append(f"- {text[:300]}{engagement}")
                    else:
                        section_lines.append(f"- {str(item)[:300]}")
                        
            elif isinstance(items, dict):
                # For structured data like Google Trends
                section_lines.append(f"Data: {str(items)[:500]}")
            
            sections.append("\n".join(section_lines))
        
        return "\n".join(sections)
    
    def get_mock_data(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Return mock analysis data"""
        return [{
            "text": MockProvider()._generate_mock_analysis(query),
            "provider": "mock",
            "prompt_type": "analysis"
        }]


# Register connector
def _register():
    try:
        from . import register_connector
        register_connector("llm", LLMConnector)
    except ImportError:
        pass

_register()


# Convenience export
def get_llm_connector(config: Dict = None) -> LLMConnector:
    """Get an LLM connector instance"""
    return LLMConnector(config)
