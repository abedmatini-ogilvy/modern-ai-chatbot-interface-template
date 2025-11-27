"""
Demo 5: Trend Research System (Real APIs Version)
Multi-Source Intelligence for Marketing Agencies

This version uses REAL API integrations with:
- Graceful failure handling (skips unavailable APIs)
- Custom question input
- Clear status messages for each API
- Production-ready error handling

Setup: See DEMO5_REAL_APIS_GUIDE.md for API configuration
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
import time
from datetime import datetime

# Try to import real APIs, fallback to mock if not available
try:
    from api_connectors_real import get_real_apis
    USE_REAL_APIS = True
except ImportError:
    from api_connectors_mock import get_mock_apis
    USE_REAL_APIS = False
    st.warning("⚠️ Real APIs not configured. Using mock data. See DEMO5_REAL_APIS_GUIDE.md")

load_dotenv()

st.set_page_config(
    page_title="Demo 5: Trend Research System (Real APIs)",
    page_icon="📊",
    layout="wide"
)

def get_azure_client():
    """Initialize Azure OpenAI client"""
    api_key = os.getenv("AZURE_AI_API_KEY")
    endpoint = os.getenv("AZURE_AI_ENDPOINT")
    
    if not endpoint or not api_key:
        return None
    
    if 'cognitiveservices' in endpoint:
        return OpenAI(
            base_url=endpoint,
            api_key=api_key
        )
    else:
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        return AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

# Pre-configured research questions
RESEARCH_QUESTIONS = {
    "gen_z_nigeria": {
        "title": "Gen Z Nigeria: Facebook vs Google Usage",
        "question": "Why does Gen Z in Nigeria appear to use Facebook for community and content discovery, while using Google primarily for functional, task-based searches?",
        "focus": "Social behavior patterns, platform preferences, user motivations",
        "search_terms": ["Gen Z Nigeria Facebook", "Nigeria Google usage", "Nigerian social media behavior"]
    },
    "detty_december": {
        "title": "Detty December Tourism Analysis",
        "question": "Beyond the parties, what are the core drivers and frustrations for the diaspora and domestic tourists participating in 'Detty December' in Nigeria and Ghana?",
        "focus": "Tourism motivations, pain points, diaspora engagement",
        "search_terms": ["Detty December Nigeria Ghana", "Diaspora tourism Africa", "December tourism West Africa"]
    },
    "creator_economy": {
        "title": "African Creator Economy Challenges",
        "question": "What are the primary financial challenges and unmet needs of emerging creators and gamers in key African markets?",
        "focus": "Monetization barriers, infrastructure gaps, creator pain points",
        "search_terms": ["African creators challenges", "African gamers monetization", "Creator economy Africa"]
    },
    "mpesa_competition": {
        "title": "M-Pesa Market Dominance Analysis",
        "question": "What are the primary drivers of M-Pesa's dominance in East Africa, and what specific user frustrations or unmet needs could a competitor leverage to capture market share among the digital-native population?",
        "focus": "Competitive analysis, user pain points, market opportunities",
        "search_terms": ["M-Pesa dominance East Africa", "Mobile money Kenya", "M-Pesa competition"]
    }
}

# Agent definitions
AGENTS = {
    "social_media": {
        "name": "Social Media Intelligence Agent",
        "icon": "📱",
        "color": "#4ECDC4",
    },
    "trends": {
        "name": "Trends Analysis Agent",
        "icon": "📈",
        "color": "#45B7D1",
    },
    "web_intelligence": {
        "name": "Web Intelligence Agent",
        "icon": "🌐",
        "color": "#96CEB4",
    },
    "insight_analyst": {
        "name": "Insight Analyst Agent",
        "icon": "🔍",
        "color": "#FFEAA7",
    },
    "report_generator": {
        "name": "Report Generator Agent",
        "icon": "📄",
        "color": "#DFE6E9",
    }
}

def collect_social_media_data(query, apis, failed_apis):
    """Phase 1: Collect data from social media platforms with error handling"""
    results = {}
    
    # Twitter/X
    with st.status("🐦 Collecting Twitter/X data...", expanded=True) as status:
        if apis["twitter"].available:
            st.write("Searching tweets...")
            twitter_data = apis["twitter"].search_tweets(query, max_results=50)
            if twitter_data:
                results["twitter"] = twitter_data
                st.write(f"✅ Found {twitter_data['total_results']} tweets")
                st.write(f"📊 Sentiment: {twitter_data['metrics']['sentiment_breakdown']}")
                status.update(label="✅ Twitter/X data collected", state="complete")
            else:
                st.warning("⚠️ Twitter API returned no results")
                failed_apis.append("Twitter/X")
                status.update(label="⚠️ Twitter/X - No results", state="error")
        else:
            st.warning("❌ Twitter API not configured")
            failed_apis.append("Twitter/X")
            status.update(label="❌ Twitter/X not available", state="error")
    
    # TikTok
    with st.status("🎵 Collecting TikTok data...", expanded=True) as status:
        if apis["tiktok"].available:
            st.write("Searching videos...")
            tiktok_data = apis["tiktok"].search_videos(query, max_results=30)
            if tiktok_data:
                results["tiktok"] = tiktok_data
                st.write(f"✅ Found {tiktok_data['total_results']} videos")
                st.write(f"👁️ Total views: {tiktok_data['metrics']['total_views']:,}")
                status.update(label="✅ TikTok data collected", state="complete")
            else:
                st.warning("⚠️ TikTok API returned no results")
                failed_apis.append("TikTok")
                status.update(label="⚠️ TikTok - No results", state="error")
        else:
            st.warning("❌ TikTok API not configured")
            failed_apis.append("TikTok")
            status.update(label="❌ TikTok not available", state="error")
    
    # Reddit
    with st.status("💬 Collecting Reddit data...", expanded=True) as status:
        if apis["reddit"].available:
            st.write("Searching posts and discussions...")
            reddit_data = apis["reddit"].search_posts(query, max_results=50)
            if reddit_data:
                results["reddit"] = reddit_data
                st.write(f"✅ Found {reddit_data['total_results']} posts")
                st.write(f"💭 Total comments: {reddit_data['metrics']['total_comments']:,}")
                status.update(label="✅ Reddit data collected", state="complete")
            else:
                st.warning("⚠️ Reddit API returned no results")
                failed_apis.append("Reddit")
                status.update(label="⚠️ Reddit - No results", state="error")
        else:
            st.warning("❌ Reddit API not configured")
            failed_apis.append("Reddit")
            status.update(label="❌ Reddit not available", state="error")
    
    return results

def collect_trends_data(query, apis, failed_apis):
    """Phase 1: Collect Google Trends data with error handling"""
    with st.status("📈 Analyzing Google Trends...", expanded=True) as status:
        if apis["google_trends"].available:
            st.write("Fetching search trends...")
            trends_data = apis["google_trends"].get_trends(query)
            if trends_data:
                st.write(f"✅ Search volume index: {trends_data['search_volume_index']}")
                st.write(f"📊 Status: {trends_data['trending_status']}")
                if trends_data.get('regional_interest'):
                    top_region = list(trends_data['regional_interest'].keys())[0] if trends_data['regional_interest'] else "N/A"
                    st.write(f"🌍 Top region: {top_region}")
                status.update(label="✅ Trends data collected", state="complete")
                return trends_data
            else:
                st.warning("⚠️ Google Trends returned no results")
                failed_apis.append("Google Trends")
                status.update(label="⚠️ Google Trends - No results", state="error")
                return None
        else:
            st.warning("❌ Google Trends not configured")
            failed_apis.append("Google Trends")
            status.update(label="❌ Google Trends not available", state="error")
            return None

def collect_web_intelligence(query, apis, failed_apis):
    """Phase 1: Collect web search data with error handling"""
    with st.status("🌐 Gathering web intelligence...", expanded=True) as status:
        if apis["web_search"].available:
            st.write("Searching web sources...")
            search_data = apis["web_search"].search(query, max_results=20)
            if search_data:
                st.write(f"✅ Found {search_data['total_results']} articles/posts")
                st.write(f"📰 News articles: {search_data['metrics']['news_articles']}")
                st.write(f"📝 Blog posts: {search_data['metrics']['blog_posts']}")
                status.update(label="✅ Web intelligence collected", state="complete")
                return search_data
            else:
                st.warning("⚠️ Web Search returned no results")
                failed_apis.append("Web Search")
                status.update(label="⚠️ Web Search - No results", state="error")
                return None
        else:
            st.warning("❌ Web Search API not configured")
            failed_apis.append("Web Search")
            status.update(label="❌ Web Search not available", state="error")
            return None

def create_data_summary(all_data, question):
    """Create a summary of collected data for analysis"""
    summary_parts = [f"Research Question: {question}\n"]
    
    # Social media data
    if "social_media" in all_data and all_data["social_media"]:
        social = all_data["social_media"]
        
        if "twitter" in social:
            summary_parts.append(f"""
TWITTER/X DATA:
- Total tweets: {social['twitter']['total_results']}
- Sentiment: {social['twitter']['metrics']['sentiment_breakdown']}
- Top hashtags: {social['twitter']['metrics']['top_hashtags']}
""")
        
        if "tiktok" in social:
            summary_parts.append(f"""
TIKTOK DATA:
- Total videos: {social['tiktok']['total_results']}
- Total views: {social['tiktok']['metrics']['total_views']:,}
- Engagement rate: {social['tiktok']['metrics']['total_engagement_rate']}%
""")
        
        if "reddit" in social:
            summary_parts.append(f"""
REDDIT DATA:
- Total posts: {social['reddit']['total_results']}
- Total comments: {social['reddit']['metrics']['total_comments']}
- Top subreddits: {social['reddit']['metrics']['top_subreddits']}
""")
    
    # Trends data
    if "trends" in all_data and all_data["trends"]:
        trends = all_data["trends"]
        summary_parts.append(f"""
GOOGLE TRENDS:
- Search volume index: {trends['search_volume_index']}
- Trending status: {trends['trending_status']}
- Regional interest: {trends.get('regional_interest', 'N/A')}
""")
    
    # Web intelligence
    if "web_intelligence" in all_data and all_data["web_intelligence"]:
        web = all_data["web_intelligence"]
        summary_parts.append(f"""
WEB INTELLIGENCE:
- Total sources: {web['total_results']}
- News articles: {web['metrics']['news_articles']}
- Blog posts: {web['metrics']['blog_posts']}
""")
    
    return "\n".join(summary_parts)

def analyze_insights(client, model, all_data, question):
    """Phase 2: Analyze all collected data for insights"""
    agent = AGENTS["insight_analyst"]
    
    with st.status(f"{agent['icon']} {agent['name']} analyzing data...", expanded=True) as status:
        st.write("Processing multi-source data...")
        
        # Count data points
        data_points = 0
        if "social_media" in all_data:
            for platform in all_data["social_media"].values():
                data_points += platform.get('total_results', 0)
        if "trends" in all_data and all_data["trends"]:
            data_points += 1
        if "web_intelligence" in all_data and all_data["web_intelligence"]:
            data_points += all_data["web_intelligence"].get('total_results', 0)
        
        st.write(f"- Analyzing {data_points} data points")
        
        data_summary = create_data_summary(all_data, question)
        
        analysis_prompt = f"""{data_summary}

Analyze this data and identify:
1. Key patterns and trends
2. Audience behavior insights
3. Platform-specific findings
4. Market opportunities
5. Strategic implications for marketing
"""
        
        try:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_AI_MODEL_NAME", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an Insight Analyst Agent for a marketing agency. Synthesize data from multiple sources to identify patterns, trends, and actionable insights."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            insights = response.choices[0].message.content
            st.write("✅ Analysis complete")
            status.update(label=f"✅ {agent['name']} completed analysis", state="complete")
            
            return insights
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            return None

def generate_report(client, model, all_data, insights, question):
    """Phase 2: Generate comprehensive marketing report"""
    agent = AGENTS["report_generator"]
    
    with st.status(f"{agent['icon']} {agent['name']} creating report...", expanded=True) as status:
        st.write("Synthesizing findings...")
        st.write("Creating executive summary...")
        st.write("Formatting recommendations...")
        
        data_summary = create_data_summary(all_data, question)
        
        report_prompt = f"""
Create a comprehensive marketing research report for the following question:

{question}

INSIGHTS FROM ANALYSIS:
{insights}

RAW DATA SUMMARY:
{data_summary}

Create a client-ready report with these sections:
1. EXECUTIVE SUMMARY (2-3 paragraphs)
2. KEY FINDINGS (5-7 bullet points)
3. PLATFORM INSIGHTS (for each available platform)
4. AUDIENCE DEMOGRAPHICS & BEHAVIOR
5. SENTIMENT ANALYSIS
6. ACTIONABLE RECOMMENDATIONS (5-7 specific actions)
7. DATA SOURCES & METHODOLOGY

Use professional, clear language suitable for marketing executives.
"""
        
        try:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_AI_MODEL_NAME", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are a Report Generator Agent for a marketing agency. Create comprehensive, client-ready research reports."},
                    {"role": "user", "content": report_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            report = response.choices[0].message.content
            st.write("✅ Report generated")
            status.update(label=f"✅ {agent['name']} completed report", state="complete")
            
            return report
            
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            return None

# Main UI
st.title("📊 Demo 5: Trend Research System")
st.markdown("### Multi-Source Intelligence for Marketing Agencies (Real APIs)")

if USE_REAL_APIS:
    st.success("✅ Using Real API Connectors")
else:
    st.info("ℹ️ Using Mock Data (Real APIs not configured)")

st.markdown("""
This demo showcases a sophisticated multi-agent system that:
- 🔄 **Collects data** from multiple platforms in parallel
- 🔍 **Analyzes patterns** across sources
- 📄 **Generates reports** ready for clients
- ⚠️ **Handles failures** gracefully (skips unavailable APIs)
""")

# Configuration check
client = get_azure_client()
model = os.getenv("AZURE_AI_MODEL_NAME", "gpt-4")

if not client:
    st.error("⚠️ Please configure your Azure AI credentials in the .env file")
    st.info("See .env.example for the required format")
    st.stop()

st.success(f"✅ Connected to Azure AI | Model: {model}")

# Sidebar: Agent Team & API Status
with st.sidebar:
    st.header("🤖 Research Team")
    
    st.markdown("### Phase 1: Data Collection")
    for agent_key in ["social_media", "trends", "web_intelligence"]:
        agent = AGENTS[agent_key]
        st.markdown(f"""
        <div style="background-color: {agent['color']}20; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{agent['icon']} {agent['name']}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Phase 2: Analysis & Synthesis")
    for agent_key in ["insight_analyst", "report_generator"]:
        agent = AGENTS[agent_key]
        st.markdown(f"""
        <div style="background-color: {agent['color']}20; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{agent['icon']} {agent['name']}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Status
    if USE_REAL_APIS:
        st.header("📡 API Status")
        apis = get_real_apis() if USE_REAL_APIS else get_mock_apis()
        for name, api in apis.items():
            if hasattr(api, 'available'):
                status_icon = "✅" if api.available else "❌"
                st.markdown(f"{status_icon} {api.name}")

# Main content
st.markdown("---")
st.header("📋 Research Question")

# Question input method selection
input_method = st.radio(
    "Choose input method:",
    ["Select from pre-configured questions", "Enter custom question"],
    horizontal=True
)

if input_method == "Select from pre-configured questions":
    # Pre-configured questions
    question_options = {
        key: data["title"] 
        for key, data in RESEARCH_QUESTIONS.items()
    }
    
    selected_key = st.selectbox(
        "Choose a marketing research question:",
        options=list(question_options.keys()),
        format_func=lambda x: question_options[x]
    )
    
    selected_question = RESEARCH_QUESTIONS[selected_key]
    question_text = selected_question["question"]
    search_query = selected_question["search_terms"][0]
    
    # Display question details
    with st.expander("📄 Question Details", expanded=True):
        st.markdown(f"**Research Question:**")
        st.info(question_text)
        st.markdown(f"**Focus Areas:** {selected_question['focus']}")
        st.markdown(f"**Search Terms:** {', '.join(selected_question['search_terms'])}")

else:
    # Custom question input
    st.markdown("### Enter Your Research Question")
    
    question_text = st.text_area(
        "Research Question:",
        placeholder="e.g., What are the emerging trends in African e-commerce?",
        height=100
    )
    
    search_query = st.text_input(
        "Search Query (for APIs):",
        placeholder="e.g., African e-commerce trends",
        help="This will be used to search across all platforms"
    )
    
    if question_text and search_query:
        with st.expander("📄 Your Question", expanded=True):
            st.markdown(f"**Research Question:**")
            st.info(question_text)
            st.markdown(f"**Search Query:** {search_query}")

# Start research button
col1, col2 = st.columns([1, 3])
with col1:
    can_start = (question_text and search_query) if input_method == "Enter custom question" else True
    start_research = st.button("🚀 Start Research", type="primary", use_container_width=True, disabled=not can_start)

if not can_start and input_method == "Enter custom question":
    st.warning("⚠️ Please enter both a research question and search query to continue")

if start_research:
    st.markdown("---")
    st.header("🔬 Research in Progress")
    
    # Initialize APIs
    apis = get_real_apis() if USE_REAL_APIS else get_mock_apis()
    
    # Track failed APIs
    failed_apis = []
    
    # Store start time
    start_time = time.time()
    
    # Phase 1: Parallel Data Collection
    st.subheader("📊 Phase 1: Data Collection (Parallel Execution)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📱 Social Media")
        social_media_data = collect_social_media_data(search_query, apis, failed_apis)
    
    with col2:
        st.markdown("#### 📈 Trends")
        trends_data = collect_trends_data(search_query, apis, failed_apis)
    
    with col3:
        st.markdown("#### 🌐 Web Intelligence")
        web_intelligence_data = collect_web_intelligence(search_query, apis, failed_apis)
    
    # Combine all data
    all_data = {}
    if social_media_data:
        all_data["social_media"] = social_media_data
    if trends_data:
        all_data["trends"] = trends_data
    if web_intelligence_data:
        all_data["web_intelligence"] = web_intelligence_data
    
    # Show failed APIs summary
    if failed_apis:
        st.warning(f"⚠️ **APIs that didn't return results:** {', '.join(failed_apis)}")
        st.info("ℹ️ Research will continue with available data sources")
    
    # Check if we have any data
    if not all_data:
        st.error("❌ No data collected from any API. Cannot proceed with analysis.")
        st.info("💡 Please configure at least one API. See DEMO5_REAL_APIS_GUIDE.md")
        st.stop()
    
    st.success(f"✅ Phase 1 Complete: Data collected from {len(all_data)} source(s)")
    
    # Phase 2: Sequential Analysis & Synthesis
    st.markdown("---")
    st.subheader("🔍 Phase 2: Analysis & Synthesis (Sequential Execution)")
    
    # Step 1: Analyze insights
    insights = analyze_insights(client, model, all_data, question_text)
    
    if insights:
        # Step 2: Generate report
        report = generate_report(client, model, all_data, insights, question_text)
        
        if report:
            # Calculate execution time
            execution_time = time.time() - start_time
            
            st.success(f"✅ Phase 2 Complete: Report generated in {execution_time:.1f} seconds")
            
            # Display final report
            st.markdown("---")
            st.header("📄 Final Research Report")
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                sources_count = len(all_data)
                st.metric("Data Sources", f"{sources_count} platform(s)")
            with col2:
                total_data_points = 0
                if "social_media" in all_data:
                    for platform in all_data["social_media"].values():
                        total_data_points += platform.get('total_results', 0)
                if "web_intelligence" in all_data:
                    total_data_points += all_data["web_intelligence"].get('total_results', 0)
                st.metric("Data Points", f"{total_data_points:,}")
            with col3:
                st.metric("Execution Time", f"{execution_time:.1f}s")
            with col4:
                agents_used = 2 + sources_count  # Analyst + Generator + data collectors
                st.metric("Agents Used", str(agents_used))
            with col5:
                st.metric("Failed APIs", str(len(failed_apis)))
            
            # Display report
            st.markdown(report)
            
            # Download options
            st.markdown("---")
            st.subheader("💾 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                export_data = {
                    "question": question_text,
                    "search_query": search_query,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "data_sources": all_data,
                    "failed_apis": failed_apis,
                    "insights": insights,
                    "report": report
                }
                
                json_str = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download Full Data (JSON)",
                    data=json_str,
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Text report export
                report_text = f"""
MARKETING RESEARCH REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESEARCH QUESTION:
{question_text}

SEARCH QUERY:
{search_query}

{report}

---
Data Sources: {', '.join([k.replace('_', ' ').title() for k in all_data.keys()])}
Failed APIs: {', '.join(failed_apis) if failed_apis else 'None'}
Total Data Points: {total_data_points:,}
Execution Time: {execution_time:.1f} seconds
"""
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=report_text,
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("---")
st.markdown("""
### 🎯 What This Demo Shows

**Agentic Patterns:**
- ✅ **Parallel Execution** - Multiple agents collecting data simultaneously
- ✅ **Sequential Processing** - Ordered analysis and synthesis
- ✅ **Multi-Source Aggregation** - Combining data from multiple platforms
- ✅ **Graceful Degradation** - Continues even if some APIs fail
- ✅ **Error Handling** - Clear status for each API

**Real-World Application:**
Marketing agencies can use this pattern to:
- Conduct comprehensive market research
- Analyze social media trends
- Generate client-ready reports
- Handle API failures gracefully

**Production Features:**
- ✅ Real API integrations (Twitter, Reddit, Google Trends, Bing)
- ✅ Custom question input
- ✅ Graceful failure handling
- ✅ Clear error messages
- ✅ Export options (JSON + TXT)
""")
