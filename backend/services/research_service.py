"""
Research Service - Core Research Orchestration Logic

This service extracts the multi-agent research logic from the Streamlit app
and makes it reusable as a Python service without UI dependencies.

It orchestrates:
- Phase 1: Parallel data collection from 5 platforms
- Phase 2: Sequential analysis and report generation (using Gemini or other LLMs)
- Progress tracking and updates
- Error handling and graceful degradation
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from openai import AzureOpenAI, OpenAI
import os

# Configure logging
logger = logging.getLogger(__name__)

from models.research_models import (
    ResearchPhase,
    AgentStatus,
    ProgressUpdate,
    ResearchResultResponse
)

# Import API connectors
from api_connectors_mock import get_mock_apis

try:
    from api_connectors_real import get_real_apis
    USE_REAL_APIS = True
except ImportError:
    USE_REAL_APIS = False

# Import LLM connector for analysis
try:
    from connectors import get_connector, ConnectorStatus
    LLM_CONNECTOR_AVAILABLE = True
except ImportError:
    LLM_CONNECTOR_AVAILABLE = False


class ResearchService:
    """
    Service for orchestrating multi-agent trend research.
    
    This class coordinates the entire research workflow:
    1. Data collection from multiple platforms in parallel
    2. Data analysis and insight extraction
    3. Comprehensive report generation
    4. Progress tracking and updates
    """
    
    # Pre-configured research questions (from Streamlit app)
    RESEARCH_QUESTIONS = {
        "gen_z_nigeria": {
            "id": "gen_z_nigeria",
            "title": "Gen Z Nigeria: Facebook vs Google Usage",
            "question": "Why does Gen Z in Nigeria appear to use Facebook for community and content discovery, while using Google primarily for functional, task-based searches?",
            "focus": "Social behavior patterns, platform preferences, user motivations",
            "search_terms": ["Gen Z Nigeria Facebook", "Nigeria Google usage", "Nigerian social media behavior"]
        },
        "detty_december": {
            "id": "detty_december",
            "title": "Detty December Tourism Analysis",
            "question": "Beyond the parties, what are the core drivers and frustrations for the diaspora and domestic tourists participating in 'Detty December' in Nigeria and Ghana?",
            "focus": "Tourism motivations, pain points, diaspora engagement",
            "search_terms": ["Detty December Nigeria Ghana", "Diaspora tourism Africa", "December tourism West Africa"]
        },
        "creator_economy": {
            "id": "creator_economy",
            "title": "African Creator Economy Challenges",
            "question": "What are the primary financial challenges and unmet needs of emerging creators and gamers in key African markets?",
            "focus": "Monetization barriers, infrastructure gaps, creator pain points",
            "search_terms": ["African creators challenges", "African gamers monetization", "Creator economy Africa"]
        },
        "mpesa_competition": {
            "id": "mpesa_competition",
            "title": "M-Pesa Market Dominance Analysis",
            "question": "What are the primary drivers of M-Pesa's dominance in East Africa, and what specific user frustrations or unmet needs could a competitor leverage to capture market share among the digital-native population?",
            "focus": "Competitive analysis, user pain points, market opportunities",
            "search_terms": ["M-Pesa dominance East Africa", "Mobile money Kenya", "M-Pesa competition"]
        }
    }
    
    def __init__(self, azure_api_key: Optional[str] = None, azure_endpoint: Optional[str] = None):
        """
        Initialize the research service.
        
        Args:
            azure_api_key: Azure OpenAI API key
            azure_endpoint: Azure OpenAI endpoint
        """
        self.azure_api_key = azure_api_key or os.getenv("AZURE_AI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_AI_ENDPOINT")
        self.model_name = os.getenv("AZURE_AI_MODEL_NAME", "gpt-4")
        
        self.client = self._initialize_openai_client()
        
        # Initialize LLM connector (Gemini, etc.) as primary analysis engine
        self.llm_connector = None
        if LLM_CONNECTOR_AVAILABLE:
            try:
                self.llm_connector = get_connector("llm")
                if self.llm_connector.is_configured():
                    print("✅ LLM Connector (Gemini) configured for analysis")
                else:
                    print("⚠️ LLM Connector not configured, will use Azure OpenAI or mock")
                    self.llm_connector = None
            except Exception as e:
                print(f"⚠️ LLM Connector initialization failed: {e}")
                self.llm_connector = None
        
        # Try real APIs first, fallback to mock if not available
        if USE_REAL_APIS:
            try:
                apis = get_real_apis()
                # Check if any API is actually configured
                has_configured_api = any(
                    hasattr(api, 'available') and api.available 
                    for api in apis.values()
                )
                if has_configured_api:
                    self.apis = apis
                    self.using_mock = False
                else:
                    print("ℹ️ No real APIs configured, using mock data")
                    self.apis = get_mock_apis()
                    self.using_mock = True
            except Exception:
                self.apis = get_mock_apis()
                self.using_mock = True
        else:
            self.apis = get_mock_apis()
            self.using_mock = True
        
    def _initialize_openai_client(self):
        """Initialize Azure OpenAI client"""
        if not self.azure_endpoint or not self.azure_api_key:
            return None
        
        if 'cognitiveservices' in self.azure_endpoint:
            return OpenAI(
                base_url=self.azure_endpoint,
                api_key=self.azure_api_key
            )
        else:
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            return AzureOpenAI(
                api_key=self.azure_api_key,
                api_version=api_version,
                azure_endpoint=self.azure_endpoint
            )
    
    async def conduct_research(
        self,
        question: str,
        search_query: str,
        session_id: str,
        progress_callback: Optional[Callable] = None,
        max_results: int = 50
    ) -> ResearchResultResponse:
        """
        Conduct complete research workflow.
        
        Args:
            question: Research question to investigate
            search_query: Search query for APIs
            session_id: Unique session identifier
            progress_callback: Optional callback for progress updates
            max_results: Maximum results per API
            
        Returns:
            Complete research results
        """
        start_time = time.time()
        progress_updates = []
        failed_apis = []
        
        def add_progress(phase: ResearchPhase, agent: str, status: AgentStatus, message: str, data: Optional[Dict] = None):
            """Helper to add progress update"""
            update = ProgressUpdate(
                timestamp=datetime.now(),
                phase=phase,
                agent=agent,
                status=status,
                message=message,
                data=data
            )
            progress_updates.append(update)
            if progress_callback:
                progress_callback(update)
        
        try:
            # PHASE 1: Data Collection (Parallel)
            add_progress(ResearchPhase.DATA_COLLECTION, "Research Orchestrator", AgentStatus.RUNNING, 
                        "🔬 Starting Phase 1: Data Collection")
            
            # Collect from all platforms in parallel
            social_media_data, trends_data, web_data = await asyncio.gather(
                self._collect_social_media_data(search_query, max_results, add_progress, failed_apis),
                self._collect_trends_data(search_query, add_progress, failed_apis),
                self._collect_web_intelligence(search_query, max_results, add_progress, failed_apis),
                return_exceptions=True
            )
            
            # Combine all data
            all_data = {}
            if isinstance(social_media_data, dict) and social_media_data:
                all_data["social_media"] = social_media_data
            if isinstance(trends_data, dict) and trends_data:
                all_data["trends"] = trends_data
            if isinstance(web_data, dict) and web_data:
                all_data["web_intelligence"] = web_data
            
            # Report summary of failed APIs at end of data collection
            if failed_apis:
                unique_failed = list(set(failed_apis))  # Remove duplicates
                failed_summary = f"""
📊 **Data Collection Summary**
   ✅ Successful: {len(all_data)} source(s)
   ❌ Failed: {len(unique_failed)} API(s) - {', '.join(unique_failed)}
"""
                add_progress(ResearchPhase.DATA_COLLECTION, "Research Orchestrator", AgentStatus.COMPLETED, failed_summary)
            
            if not all_data:
                # All APIs failed - provide detailed error
                failed_list = list(set(failed_apis)) if failed_apis else ["All APIs"]
                error_msg = f"No data collected. Failed APIs: {', '.join(failed_list)}. Please check API configurations."
                add_progress(ResearchPhase.DATA_COLLECTION, "Research Orchestrator", AgentStatus.FAILED, 
                           f"❌ {error_msg}")
                raise Exception(error_msg)
            
            add_progress(ResearchPhase.DATA_COLLECTION, "Research Orchestrator", AgentStatus.COMPLETED,
                        f"✅ Phase 1 Complete: Data collected from {len(all_data)} source(s)")
            
            # Calculate total data points
            total_data_points = self._count_data_points(all_data)
            
            # PHASE 2: Analysis
            add_progress(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.RUNNING,
                        "🔍 Starting Phase 2: Analyzing collected data...")
            
            insights = await self._analyze_insights(question, all_data, add_progress)
            
            if not insights:
                raise Exception("Analysis failed")
            
            add_progress(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.COMPLETED,
                        "✅ Analysis complete")
            
            # PHASE 3: Report Generation
            add_progress(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.RUNNING,
                        "📄 Generating comprehensive report...")
            
            report = await self._generate_report(question, all_data, insights, add_progress, failed_apis)
            
            if not report:
                raise Exception("Report generation failed")
            
            add_progress(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.COMPLETED,
                        "✅ Report generated successfully")
            
            # Parse report sections
            executive_summary, key_findings, recommendations = self._parse_report_sections(report)
            
            # Create response
            execution_time = time.time() - start_time
            
            return ResearchResultResponse(
                session_id=session_id,
                question=question,
                search_query=search_query,
                phase=ResearchPhase.COMPLETED,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.now(),
                execution_time_seconds=execution_time,
                data_collected=self._create_data_summary(all_data),
                total_data_points=total_data_points,
                failed_apis=failed_apis,
                insights=insights,
                report=report,
                executive_summary=executive_summary,
                key_findings=key_findings,
                recommendations=recommendations,
                progress_updates=progress_updates
            )
            
        except Exception as e:
            add_progress(ResearchPhase.FAILED, "System", AgentStatus.FAILED,
                        f"❌ Research failed: {str(e)}")
            
            return ResearchResultResponse(
                session_id=session_id,
                question=question,
                search_query=search_query,
                phase=ResearchPhase.FAILED,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.now(),
                execution_time_seconds=time.time() - start_time,
                progress_updates=progress_updates,
                error=str(e)
            )
    
    async def _collect_social_media_data(self, query: str, max_results: int, progress_callback, failed_apis: List[str]) -> Dict:
        """Collect data from social media platforms - REAL DATA ONLY, no mocks"""
        results = {}
        
        # Twitter/X
        progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.RUNNING,
                         "🐦 Collecting Twitter/X data...")
        try:
            if hasattr(self.apis["twitter"], 'available') and not self.apis["twitter"].available:
                failed_apis.append("Twitter/X")
                progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.FAILED,
                                "❌ Twitter/X API: Not configured - missing API credentials")
            else:
                twitter_data = self.apis["twitter"].search_tweets(query, max_results=max_results)
                if twitter_data and twitter_data.get('total_results', 0) > 0:
                    # Check if this is real data (not mock) - check both top-level and in metrics
                    is_mock = (
                        twitter_data.get('connector_status') == 'mock' or 
                        twitter_data.get('data_source') == 'mock' or
                        twitter_data.get('metrics', {}).get('data_source') == 'mock'
                    )
                    if is_mock:
                        failed_apis.append("Twitter/X")
                        progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.FAILED,
                                        "❌ Twitter/X API: No real data available (API returned mock data)")
                    else:
                        results["twitter"] = twitter_data
                        # Detailed success message
                        sentiment = twitter_data.get('metrics', {}).get('sentiment_breakdown', {})
                        sample_tweet = ""
                        if twitter_data.get('tweets') and len(twitter_data['tweets']) > 0:
                            sample_tweet = twitter_data['tweets'][0].get('text', '')[:80] + "..."
                        
                        detail_msg = f"""✅ Twitter/X Intelligence Agent
   - Tweets found: {twitter_data['total_results']}
   - Sentiment: {sentiment.get('positive', 0)}% positive, {sentiment.get('neutral', 0)}% neutral, {sentiment.get('negative', 0)}% negative
   - Sample: "{sample_tweet}" """
                        progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.COMPLETED, detail_msg)
                else:
                    failed_apis.append("Twitter/X")
                    progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.FAILED,
                                    "❌ Twitter/X API: No results found for this query")
        except Exception as e:
            failed_apis.append("Twitter/X")
            error_reason = self._parse_api_error(str(e), "Twitter")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Twitter Intelligence Agent", AgentStatus.FAILED,
                            f"❌ Twitter/X API Failed\n   - Error: {error_reason}")
        
        # TikTok
        progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.RUNNING,
                         "🎵 Collecting TikTok data...")
        try:
            if hasattr(self.apis["tiktok"], 'available') and not self.apis["tiktok"].available:
                failed_apis.append("TikTok")
                progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.FAILED,
                                "❌ TikTok API: Not configured - missing API credentials")
            else:
                tiktok_data = self.apis["tiktok"].search_videos(query, max_results=max_results)
                if tiktok_data and tiktok_data.get('total_results', 0) > 0:
                    # Check if this is real data (not mock) - check both top-level and in metrics
                    is_mock = (
                        tiktok_data.get('connector_status') == 'mock' or 
                        tiktok_data.get('data_source') == 'mock' or
                        tiktok_data.get('metrics', {}).get('data_source') == 'mock'
                    )
                    if is_mock:
                        failed_apis.append("TikTok")
                        progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.FAILED,
                                        "❌ TikTok API: No real data available (API returned mock data)")
                    else:
                        results["tiktok"] = tiktok_data
                        total_views = tiktok_data.get('metrics', {}).get('total_views', 0)
                        detail_msg = f"""✅ TikTok Intelligence Agent
   - Videos found: {tiktok_data['total_results']}
   - Total views: {total_views:,}
   - Avg engagement: {tiktok_data.get('metrics', {}).get('avg_engagement', 'N/A')}"""
                        progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.COMPLETED, detail_msg)
                else:
                    failed_apis.append("TikTok")
                    progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.FAILED,
                                    "❌ TikTok API: No results found for this query")
        except Exception as e:
            failed_apis.append("TikTok")
            error_reason = self._parse_api_error(str(e), "TikTok")
            progress_callback(ResearchPhase.DATA_COLLECTION, "TikTok Intelligence Agent", AgentStatus.FAILED,
                            f"❌ TikTok API Failed\n   - Error: {error_reason}")
            logger.error(f"TikTok collection failed: {e}", exc_info=True)
        
        # Reddit
        progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.RUNNING,
                         "💬 Collecting Reddit data...")
        try:
            if hasattr(self.apis["reddit"], 'available') and not self.apis["reddit"].available:
                failed_apis.append("Reddit")
                progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.FAILED,
                                "❌ Reddit API: Not configured - missing API credentials")
                logger.warning("Reddit API not configured/available")
            else:
                logger.info(f"Calling Reddit API with query: {query}")
                reddit_data = self.apis["reddit"].search_posts(query, max_results=max_results)
                logger.info(f"Reddit returned: {reddit_data.get('total_results', 0) if reddit_data else 0} results")
                if reddit_data and reddit_data.get('total_results', 0) > 0:
                    # Check if this is real data (not mock) - check both top-level and in metrics
                    is_mock = (
                        reddit_data.get('connector_status') == 'mock' or 
                        reddit_data.get('data_source') == 'mock' or
                        reddit_data.get('metrics', {}).get('data_source') == 'mock'
                    )
                    if is_mock:
                        failed_apis.append("Reddit")
                        progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.FAILED,
                                        "❌ Reddit API: No real data available (API returned mock data)")
                    else:
                        results["reddit"] = reddit_data
                        top_subs = reddit_data.get('metrics', {}).get('top_subreddits', [])[:3]
                        sample_post = ""
                        if reddit_data.get('posts') and len(reddit_data['posts']) > 0:
                            sample_post = reddit_data['posts'][0].get('title', '')[:60] + "..."
                        
                        detail_msg = f"""✅ Reddit Intelligence Agent
   - Posts found: {reddit_data['total_results']}
   - Top subreddits: {', '.join(top_subs) if top_subs else 'N/A'}
   - Total comments: {reddit_data.get('metrics', {}).get('total_comments', 'N/A')}
   - Sample: "{sample_post}" """
                        progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.COMPLETED, detail_msg)
                else:
                    failed_apis.append("Reddit")
                    progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.FAILED,
                                    "❌ Reddit API: No results found for this query")
                    logger.warning("Reddit returned empty/None data")
        except Exception as e:
            failed_apis.append("Reddit")
            error_reason = self._parse_api_error(str(e), "Reddit")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Reddit Intelligence Agent", AgentStatus.FAILED,
                            f"❌ Reddit API Failed\n   - Error: {error_reason}")
            logger.error(f"Reddit collection failed: {e}", exc_info=True)
        
        return results
    
    async def _collect_trends_data(self, query: str, progress_callback, failed_apis: List[str]) -> Optional[Dict]:
        """Collect Google Trends data - REAL DATA ONLY, no mocks"""
        progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.RUNNING,
                         "📈 Analyzing Google Trends...")
        try:
            if hasattr(self.apis["google_trends"], 'available') and not self.apis["google_trends"].available:
                failed_apis.append("Google Trends")
                progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.FAILED,
                                "❌ Google Trends API: Not configured")
                return None
            
            trends_data = self.apis["google_trends"].get_trends(query)
            if trends_data:
                # Check if this is real data (not mock) - check both top-level and in metrics
                is_mock = (
                    trends_data.get('connector_status') == 'mock' or 
                    trends_data.get('data_source') == 'mock' or
                    trends_data.get('metrics', {}).get('data_source') == 'mock'
                )
                if is_mock:
                    failed_apis.append("Google Trends")
                    progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.FAILED,
                                    "❌ Google Trends API: No real data available (API returned mock data)")
                    return None
                
                trending_status = trends_data.get('trending_status', 'stable')
                related_queries = trends_data.get('related_queries', [])[:3]
                
                detail_msg = f"""✅ Google Trends Analysis Agent
   - Search volume index: {trends_data['search_volume_index']}
   - Trending status: {trending_status}
   - Related queries: {', '.join(related_queries) if related_queries else 'N/A'}"""
                progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.COMPLETED, detail_msg)
                return trends_data
            
            failed_apis.append("Google Trends")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.FAILED,
                            "❌ Google Trends API: No data returned for this query")
            return None
            
        except Exception as e:
            failed_apis.append("Google Trends")
            error_reason = self._parse_api_error(str(e), "Google Trends")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Trends Analysis Agent", AgentStatus.FAILED,
                            f"❌ Google Trends API Failed\n   - Error: {error_reason}")
            return None
    
    async def _collect_web_intelligence(self, query: str, max_results: int, progress_callback, failed_apis: List[str]) -> Optional[Dict]:
        """Collect web search data - REAL DATA ONLY, no mocks"""
        progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.RUNNING,
                         "🌐 Gathering web intelligence...")
        try:
            if hasattr(self.apis["web_search"], 'available') and not self.apis["web_search"].available:
                failed_apis.append("Web Search")
                progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.FAILED,
                                "❌ Web Search API: Not configured - missing API credentials")
                return None
            
            search_data = self.apis["web_search"].search(query, max_results=max_results)
            if search_data and search_data.get('total_results', 0) > 0:
                # Check if this is real data (not mock) - check both top-level and in metrics
                is_mock = (
                    search_data.get('connector_status') == 'mock' or 
                    search_data.get('data_source') == 'mock' or
                    search_data.get('metrics', {}).get('data_source') == 'mock'
                )
                if is_mock:
                    failed_apis.append("Web Search")
                    progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.FAILED,
                                    "❌ Web Search API: No real data available (API returned mock data)")
                    return None
                
                news_count = search_data.get('metrics', {}).get('news_articles', 0)
                sample_title = ""
                if search_data.get('results') and len(search_data['results']) > 0:
                    sample_title = search_data['results'][0].get('title', '')[:60] + "..."
                
                detail_msg = f"""✅ Web Intelligence Agent
   - Sources found: {search_data['total_results']}
   - News articles: {news_count}
   - Sample: "{sample_title}" """
                progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.COMPLETED, detail_msg)
                return search_data
            
            failed_apis.append("Web Search")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.FAILED,
                            "❌ Web Search API: No results found for this query")
            return None
            
        except Exception as e:
            failed_apis.append("Web Search")
            error_reason = self._parse_api_error(str(e), "Web Search")
            progress_callback(ResearchPhase.DATA_COLLECTION, "Web Intelligence Agent", AgentStatus.FAILED,
                            f"❌ Web Search API Failed\n   - Error: {error_reason}")
            logger.error(f"Web search failed: {e}", exc_info=True)
            return None
    
    def _parse_api_error(self, error_msg: str, api_name: str) -> str:
        """Parse API error message into user-friendly reason"""
        error_lower = error_msg.lower()
        
        if '401' in error_msg or 'unauthorized' in error_lower:
            return "Authentication failed - API credentials may be invalid or expired"
        elif '403' in error_msg or 'forbidden' in error_lower:
            return "Access denied - API key may lack required permissions"
        elif '429' in error_msg or 'rate limit' in error_lower or 'too many requests' in error_lower:
            return "Rate limit exceeded - too many requests, try again later"
        elif '500' in error_msg or '502' in error_msg or '503' in error_msg:
            return f"{api_name} service temporarily unavailable"
        elif 'timeout' in error_lower:
            return "Request timed out - API server not responding"
        elif 'connection' in error_lower:
            return "Connection failed - network or API server issue"
        elif 'not found' in error_lower or '404' in error_msg:
            return "API endpoint not found - may be deprecated"
        else:
            # Return a truncated version of the original error
            return error_msg[:100] + "..." if len(error_msg) > 100 else error_msg
    
    async def _analyze_insights(self, question: str, all_data: Dict, progress_callback) -> Optional[str]:
        """Analyze collected data for insights using LLM connector (Gemini) or Azure OpenAI - NO MOCK FALLBACK"""
        
        # Try LLM Connector (Gemini) first
        if self.llm_connector:
            try:
                progress_callback(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.RUNNING,
                                "🤖 Analyzing with Gemini AI...")
                logger.info("Starting analysis with LLM connector (Gemini)")
                
                data_summary = self._create_analysis_prompt(question, all_data)
                prompt = f"""You are an Insight Analyst Agent for a marketing agency. 
Synthesize data from multiple sources to identify patterns, trends, and actionable insights.

{data_summary}

Provide your analysis with:
1. Key patterns and trends identified
2. Audience behavior insights
3. Platform-specific findings
4. Market opportunities
5. Strategic implications for marketing"""
                
                result = await self.llm_connector.generate(prompt)
                logger.info(f"LLM connector returned status: {result.status}")
                
                if result.status == ConnectorStatus.SUCCESS and result.data:
                    analysis = result.data[0].get("analysis", result.data[0].get("text", ""))
                    if analysis:
                        logger.info(f"Gemini analysis successful ({len(analysis)} chars)")
                        return analysis
                
                # Fallback to Azure if Gemini fails
                logger.warning(f"Gemini returned incomplete result: {result.status}")
                progress_callback(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.RUNNING,
                                f"⚠️ Gemini analysis incomplete, trying Azure OpenAI...")
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}", exc_info=True)
                progress_callback(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.RUNNING,
                                f"⚠️ Gemini failed ({str(e)[:50]}), trying Azure OpenAI...")
        
        # Try Azure OpenAI as fallback
        if self.client:
            try:
                logger.info("Trying Azure OpenAI for analysis")
                data_summary = self._create_analysis_prompt(question, all_data)
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an Insight Analyst Agent for a marketing agency. Synthesize data from multiple sources to identify patterns, trends, and actionable insights."},
                        {"role": "user", "content": data_summary}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                logger.info("Azure OpenAI analysis successful")
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"Azure OpenAI analysis failed: {e}", exc_info=True)
                progress_callback(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.FAILED,
                                f"❌ Azure OpenAI analysis failed: {str(e)[:50]}")
                return None
        
        # No LLM available - cannot generate insights
        progress_callback(ResearchPhase.ANALYSIS, "Insight Analyst Agent", AgentStatus.FAILED,
                        "❌ No LLM available - cannot generate insights. Configure Gemini or Azure OpenAI API.")
        logger.error("No LLM configured for analysis")
        return None
    
    async def _generate_report(self, question: str, all_data: Dict, insights: str, progress_callback, failed_apis: List[str] = None) -> Optional[str]:
        """Generate comprehensive research report using LLM connector (Gemini) or Azure OpenAI - NO MOCK FALLBACK"""
        
        # Build disclaimer about data sources
        successful_sources = []
        if "social_media" in all_data:
            if "twitter" in all_data["social_media"]:
                successful_sources.append("Twitter/X")
            if "tiktok" in all_data["social_media"]:
                successful_sources.append("TikTok")
            if "reddit" in all_data["social_media"]:
                successful_sources.append("Reddit")
        if "trends" in all_data:
            successful_sources.append("Google Trends")
        if "web_intelligence" in all_data:
            successful_sources.append("Web Search")
        
        failed_sources = failed_apis or []
        
        # Create disclaimer text
        disclaimer = f"""
## DATA SOURCE DISCLAIMER
**Data successfully collected from:** {', '.join(successful_sources) if successful_sources else 'None'}
**APIs that failed or returned no data:** {', '.join(failed_sources) if failed_sources else 'None'}

This report is based ONLY on the successfully collected data sources listed above. Conclusions may be limited by missing data from failed API sources.
"""
        
        data_summary = self._create_analysis_prompt(question, all_data)
        
        report_prompt = f"""
Create a comprehensive marketing research report for the following question:

{question}

INSIGHTS FROM ANALYSIS:
{insights}

RAW DATA SUMMARY:
{data_summary}

IMPORTANT: This report should ONLY reference data from these sources: {', '.join(successful_sources)}
The following APIs failed or returned no data and should NOT be included in the analysis: {', '.join(failed_sources) if failed_sources else 'None'}

Create a client-ready report with these sections. Use EXACTLY these section headers:

## EXECUTIVE SUMMARY
Write 2-3 paragraphs summarizing the key insights. Only reference data sources that successfully returned data.

## KEY FINDINGS
- Finding 1: Description
- Finding 2: Description
(List 5-7 bullet points, each starting with "- ")

## PLATFORM INSIGHTS
Describe insights from each platform that returned data. Skip platforms that failed.

## AUDIENCE BEHAVIOR
Describe target audience demographics and behavior patterns based on available data.

## SENTIMENT ANALYSIS
Summarize the overall sentiment from the available data.

## RECOMMENDATIONS
- Recommendation 1: Specific action
- Recommendation 2: Specific action
(List 5-7 bullet points, each starting with "- ")

IMPORTANT: Use bullet points starting with "- " for KEY FINDINGS and RECOMMENDATIONS sections.
Use professional, clear language suitable for marketing executives.
Do NOT make up or assume data from sources that failed.
"""
        
        # Try LLM Connector (Gemini) first
        if self.llm_connector:
            try:
                progress_callback(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.RUNNING,
                                "🤖 Generating report with Gemini AI...")
                
                result = await self.llm_connector.generate(report_prompt)
                
                if result.status == ConnectorStatus.SUCCESS and result.data:
                    report = result.data[0].get("analysis", result.data[0].get("text", ""))
                    if report:
                        # Append disclaimer to the report
                        return report + "\n\n" + disclaimer
                
                progress_callback(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.RUNNING,
                                f"⚠️ Gemini report incomplete, trying Azure OpenAI...")
            except Exception as e:
                progress_callback(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.RUNNING,
                                f"⚠️ Gemini failed ({str(e)[:50]}), trying Azure OpenAI...")
        
        # Try Azure OpenAI as fallback
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a Report Generator Agent for a marketing agency. Create comprehensive, client-ready research reports."},
                        {"role": "user", "content": report_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
                
                report = response.choices[0].message.content
                # Append disclaimer to the report
                return report + "\n\n" + disclaimer
                
            except Exception as e:
                progress_callback(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.FAILED,
                                f"❌ Azure OpenAI report failed: {str(e)[:50]}")
                return None
        
        # No LLM available - cannot generate report
        progress_callback(ResearchPhase.REPORT_GENERATION, "Report Generator Agent", AgentStatus.FAILED,
                        "❌ No LLM available - cannot generate report. Configure Gemini or Azure OpenAI API.")
        logger.error("No LLM configured for report generation")
        return None
    
    def _create_analysis_prompt(self, question: str, all_data: Dict) -> str:
        """Create analysis prompt from collected data"""
        parts = [f"Research Question: {question}\n"]
        
        # Social media data
        if "social_media" in all_data:
            social = all_data["social_media"]
            if "twitter" in social:
                parts.append(f"\nTWITTER/X DATA:\n- Total tweets: {social['twitter']['total_results']}\n- Sentiment: {social['twitter']['metrics']['sentiment_breakdown']}")
            if "tiktok" in social:
                parts.append(f"\nTIKTOK DATA:\n- Total videos: {social['tiktok']['total_results']}\n- Total views: {social['tiktok']['metrics']['total_views']:,}")
            if "reddit" in social:
                parts.append(f"\nREDDIT DATA:\n- Total posts: {social['reddit']['total_results']}\n- Total comments: {social['reddit']['metrics']['total_comments']}")
        
        # Trends data
        if "trends" in all_data:
            trends = all_data["trends"]
            parts.append(f"\nGOOGLE TRENDS:\n- Search volume index: {trends['search_volume_index']}\n- Status: {trends['trending_status']}")
        
        # Web intelligence
        if "web_intelligence" in all_data:
            web = all_data["web_intelligence"]
            parts.append(f"\nWEB INTELLIGENCE:\n- Total sources: {web['total_results']}\n- News articles: {web['metrics']['news_articles']}")
        
        parts.append("\nAnalyze this data and identify:\n1. Key patterns and trends\n2. Audience behavior insights\n3. Platform-specific findings\n4. Market opportunities\n5. Strategic implications for marketing")
        
        return "\n".join(parts)
    
    def _create_data_summary(self, all_data: Dict) -> Dict[str, Any]:
        """Create summary of collected data with all expected fields"""
        # Always include all expected platforms with defaults
        # This ensures frontend doesn't crash on missing fields
        summary = {
            "social_media": {
                "twitter": {"total_results": 0},
                "tiktok": {"total_results": 0},
                "reddit": {"total_results": 0}
            },
            "web_intelligence": {
                "total_results": 0
            },
            "trends": {
                "search_volume_index": 0,
                "trending_status": "unknown"
            }
        }
        
        # Override with actual data where available
        if "social_media" in all_data:
            for platform, data in all_data["social_media"].items():
                if platform in summary["social_media"]:
                    summary["social_media"][platform] = {"total_results": data.get("total_results", 0)}
        
        if "trends" in all_data:
            summary["trends"] = {
                "search_volume_index": all_data["trends"].get("search_volume_index", 0),
                "trending_status": all_data["trends"].get("trending_status", "unknown")
            }
        
        if "web_intelligence" in all_data:
            summary["web_intelligence"] = {
                "total_results": all_data["web_intelligence"].get("total_results", 0)
            }
        
        return summary
    
    def _count_data_points(self, all_data: Dict) -> int:
        """Count total data points collected"""
        count = 0
        
        if "social_media" in all_data:
            for platform_data in all_data["social_media"].values():
                count += platform_data.get("total_results", 0)
        
        if "web_intelligence" in all_data:
            count += all_data["web_intelligence"].get("total_results", 0)
        
        if "trends" in all_data:
            count += 1  # Trends counts as 1 data point
        
        return count

    def _parse_report_sections(self, report: str) -> tuple:
        """Parse report into sections for multi-message display"""
        import re
        
        executive_summary = None
        key_findings = []
        recommendations = []
        
        lines = report.split('\n')
        current_section = None
        
        # Pattern for numbered or bulleted items: "1." or "- " or "* " or "• "
        list_item_pattern = re.compile(r'^(\d+[\.\)]\s*|\s*[-*•]\s*)')
        
        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            # Detect section headers
            if 'EXECUTIVE SUMMARY' in line_upper:
                current_section = 'summary'
                continue
            elif 'KEY FINDINGS' in line_upper or 'KEY INSIGHTS' in line_upper:
                current_section = 'findings'
                continue
            elif 'RECOMMENDATION' in line_upper or 'ACTIONABLE' in line_upper:
                current_section = 'recommendations'
                continue
            elif 'PLATFORM INSIGHTS' in line_upper or 'AUDIENCE' in line_upper or 'SENTIMENT' in line_upper or 'METHODOLOGY' in line_upper or 'DATA SOURCES' in line_upper:
                # These are other sections we don't extract separately
                current_section = 'other'
                continue
            elif line_stripped.startswith('#'):
                # Any markdown header resets the section
                current_section = None
                continue
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Process content based on current section
            if current_section == 'summary':
                # Executive summary is paragraph text
                if executive_summary is None:
                    executive_summary = line_stripped
                else:
                    executive_summary += ' ' + line_stripped
                    
            elif current_section == 'findings':
                # Key findings are list items
                match = list_item_pattern.match(line_stripped)
                if match:
                    # Remove the number/bullet prefix
                    finding = line_stripped[match.end():].strip()
                    # Skip if it looks like a sub-section header
                    if finding and not finding.endswith(':') and len(finding) > 10:
                        key_findings.append(finding)
                elif line_stripped.startswith('**') and line_stripped.endswith('**'):
                    # Bold text might be a finding
                    finding = line_stripped.strip('*').strip()
                    if finding and len(finding) > 10:
                        key_findings.append(finding)
                        
            elif current_section == 'recommendations':
                # Recommendations are list items
                match = list_item_pattern.match(line_stripped)
                if match:
                    rec = line_stripped[match.end():].strip()
                    # Skip sub-section headers and very short items
                    if rec and not rec.endswith(':') and len(rec) > 10:
                        recommendations.append(rec)
        
        # Limit to reasonable counts
        key_findings = key_findings[:10] if key_findings else None
        recommendations = recommendations[:10] if recommendations else None
        
        return executive_summary, key_findings, recommendations
    
    @classmethod
    def get_research_questions(cls) -> List[Dict[str, Any]]:
        """Get list of pre-configured research questions"""
        return list(cls.RESEARCH_QUESTIONS.values())
    
    @classmethod
    def get_research_question(cls, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific research question by ID"""
        return cls.RESEARCH_QUESTIONS.get(question_id)
