"""
Demo 5: Trend Research System
Multi-Source Intelligence for Marketing Agencies

This demo showcases:
- Parallel multi-agent data collection
- Sequential analysis and synthesis
- Multi-source data aggregation
- Comprehensive market research reports
- Complex orchestration patterns

Architecture: 6 agents in 2 phases
Phase 1 (Parallel): Social Media Agent, Trends Agent, Web Intelligence Agent
Phase 2 (Sequential): Insight Analyst Agent, Report Generator Agent
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
import time
from datetime import datetime
from api_connectors_mock import get_mock_apis

load_dotenv()

st.set_page_config(
    page_title="Demo 5: Trend Research System",
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

# Research questions for marketing agencies
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
    "orchestrator": {
        "name": "Research Orchestrator",
        "icon": "🎯",
        "color": "#FF6B6B",
        "role": "coordinator",
        "system_prompt": """You are a Research Orchestrator for a marketing agency.
Your role is to coordinate multi-source research projects and ensure comprehensive data collection.
Break down research questions into specific data collection tasks for specialized agents."""
    },
    "social_media": {
        "name": "Social Media Intelligence Agent",
        "icon": "📱",
        "color": "#4ECDC4",
        "role": "data_collector",
        "system_prompt": """You are a Social Media Intelligence Agent specializing in Twitter/X, TikTok, and Reddit analysis.
Analyze social media data for trends, sentiment, engagement patterns, and audience insights.
Focus on actionable insights for marketing strategies."""
    },
    "trends": {
        "name": "Trends Analysis Agent",
        "icon": "📈",
        "color": "#45B7D1",
        "role": "data_collector",
        "system_prompt": """You are a Trends Analysis Agent specializing in Google Trends data.
Analyze search trends, regional interest, related queries, and temporal patterns.
Identify rising trends and seasonal patterns relevant to marketing campaigns."""
    },
    "web_intelligence": {
        "name": "Web Intelligence Agent",
        "icon": "🌐",
        "color": "#96CEB4",
        "role": "data_collector",
        "system_prompt": """You are a Web Intelligence Agent specializing in web search and content analysis.
Analyze news articles, blog posts, reports, and online discussions.
Extract key themes, expert opinions, and market signals."""
    },
    "insight_analyst": {
        "name": "Insight Analyst Agent",
        "icon": "🔍",
        "color": "#FFEAA7",
        "role": "analyst",
        "system_prompt": """You are an Insight Analyst Agent for a marketing agency.
Synthesize data from multiple sources to identify patterns, trends, and actionable insights.
Focus on: audience behavior, market opportunities, competitive dynamics, and strategic recommendations."""
    },
    "report_generator": {
        "name": "Report Generator Agent",
        "icon": "📄",
        "color": "#DFE6E9",
        "role": "synthesizer",
        "system_prompt": """You are a Report Generator Agent for a marketing agency.
Create comprehensive, client-ready research reports with:
- Executive Summary
- Key Findings
- Platform-specific Insights
- Audience Demographics
- Sentiment Analysis
- Actionable Recommendations
- Data Sources

Use clear, professional language suitable for marketing executives."""
    }
}

def collect_social_media_data(question_data, apis):
    """Phase 1: Collect data from social media platforms"""
    results = {}
    
    # Twitter/X
    with st.status("🐦 Collecting Twitter/X data...", expanded=True) as status:
        st.write("Searching tweets...")
        twitter_data = apis["twitter"].search_tweets(question_data["search_terms"][0], max_results=50)
        results["twitter"] = twitter_data
        st.write(f"✅ Found {twitter_data['total_results']} tweets")
        st.write(f"📊 Sentiment: {twitter_data['metrics']['sentiment_breakdown']}")
        status.update(label="✅ Twitter/X data collected", state="complete")
    
    # TikTok
    with st.status("🎵 Collecting TikTok data...", expanded=True) as status:
        st.write("Searching videos...")
        tiktok_data = apis["tiktok"].search_videos(question_data["search_terms"][0], max_results=30)
        results["tiktok"] = tiktok_data
        st.write(f"✅ Found {tiktok_data['total_results']} videos")
        st.write(f"👁️ Total views: {tiktok_data['metrics']['total_views']:,}")
        status.update(label="✅ TikTok data collected", state="complete")
    
    # Reddit
    with st.status("💬 Collecting Reddit data...", expanded=True) as status:
        st.write("Searching posts and discussions...")
        reddit_data = apis["reddit"].search_posts(question_data["search_terms"][0], max_results=50)
        results["reddit"] = reddit_data
        st.write(f"✅ Found {reddit_data['total_results']} posts")
        st.write(f"💭 Total comments: {reddit_data['metrics']['total_comments']:,}")
        status.update(label="✅ Reddit data collected", state="complete")
    
    return results

def collect_trends_data(question_data, apis):
    """Phase 1: Collect Google Trends data"""
    with st.status("📈 Analyzing Google Trends...", expanded=True) as status:
        st.write("Fetching search trends...")
        trends_data = apis["google_trends"].get_trends(question_data["search_terms"][0])
        st.write(f"✅ Search volume index: {trends_data['search_volume_index']}")
        st.write(f"📊 Status: {trends_data['trending_status']}")
        st.write(f"🌍 Top region: {list(trends_data['regional_interest'].keys())[0]}")
        status.update(label="✅ Trends data collected", state="complete")
    
    return trends_data

def collect_web_intelligence(question_data, apis):
    """Phase 1: Collect web search data"""
    with st.status("🌐 Gathering web intelligence...", expanded=True) as status:
        st.write("Searching web sources...")
        search_data = apis["web_search"].search(question_data["search_terms"][0], max_results=20)
        st.write(f"✅ Found {search_data['total_results']} articles/posts")
        st.write(f"📰 News articles: {search_data['metrics']['news_articles']}")
        st.write(f"📝 Blog posts: {search_data['metrics']['blog_posts']}")
        status.update(label="✅ Web intelligence collected", state="complete")
    
    return search_data

def analyze_insights(client, model, all_data, question_data):
    """Phase 2: Analyze all collected data for insights"""
    agent = AGENTS["insight_analyst"]
    
    with st.status(f"{agent['icon']} {agent['name']} analyzing data...", expanded=True) as status:
        st.write("Processing multi-source data...")
        st.write(f"- {all_data['social_media']['twitter']['total_results']} tweets")
        st.write(f"- {all_data['social_media']['tiktok']['total_results']} TikTok videos")
        st.write(f"- {all_data['social_media']['reddit']['total_results']} Reddit posts")
        st.write(f"- Google Trends data")
        st.write(f"- {all_data['web_intelligence']['total_results']} web sources")
        
        # Create analysis prompt
        data_summary = f"""
Research Question: {question_data['question']}

TWITTER/X DATA:
- Total tweets: {all_data['social_media']['twitter']['total_results']}
- Sentiment: {all_data['social_media']['twitter']['metrics']['sentiment_breakdown']}
- Top hashtags: {all_data['social_media']['twitter']['metrics']['top_hashtags']}
- Geographic distribution: {all_data['social_media']['twitter']['metrics']['geographic_distribution']}

TIKTOK DATA:
- Total videos: {all_data['social_media']['tiktok']['total_results']}
- Total views: {all_data['social_media']['tiktok']['metrics']['total_views']:,}
- Engagement rate: {all_data['social_media']['tiktok']['metrics']['total_engagement_rate']}%
- Age demographics: {all_data['social_media']['tiktok']['metrics']['age_demographics']}

REDDIT DATA:
- Total posts: {all_data['social_media']['reddit']['total_results']}
- Total comments: {all_data['social_media']['reddit']['metrics']['total_comments']}
- Top subreddits: {all_data['social_media']['reddit']['metrics']['top_subreddits']}
- Discussion intensity: {all_data['social_media']['reddit']['metrics']['discussion_intensity']}

GOOGLE TRENDS:
- Search volume index: {all_data['trends']['search_volume_index']}
- Trending status: {all_data['trends']['trending_status']}
- Regional interest: {all_data['trends']['regional_interest']}
- Related queries: {all_data['trends']['related_queries']}

WEB INTELLIGENCE:
- Total sources: {all_data['web_intelligence']['total_results']}
- News articles: {all_data['web_intelligence']['metrics']['news_articles']}
- Blog posts: {all_data['web_intelligence']['metrics']['blog_posts']}
- Top domains: {all_data['web_intelligence']['metrics']['top_domains']}

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
                    {"role": "system", "content": agent["system_prompt"]},
                    {"role": "user", "content": data_summary}
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

def generate_report(client, model, all_data, insights, question_data):
    """Phase 2: Generate comprehensive marketing report"""
    agent = AGENTS["report_generator"]
    
    with st.status(f"{agent['icon']} {agent['name']} creating report...", expanded=True) as status:
        st.write("Synthesizing findings...")
        st.write("Creating executive summary...")
        st.write("Formatting recommendations...")
        
        report_prompt = f"""
Create a comprehensive marketing research report for the following question:

{question_data['question']}

INSIGHTS FROM ANALYSIS:
{insights}

RAW DATA SUMMARY:
- Twitter: {all_data['social_media']['twitter']['total_results']} tweets, {all_data['social_media']['twitter']['metrics']['sentiment_breakdown']}
- TikTok: {all_data['social_media']['tiktok']['total_results']} videos, {all_data['social_media']['tiktok']['metrics']['total_views']:,} views
- Reddit: {all_data['social_media']['reddit']['total_results']} posts, {all_data['social_media']['reddit']['metrics']['total_comments']} comments
- Google Trends: Index {all_data['trends']['search_volume_index']}, Status: {all_data['trends']['trending_status']}
- Web Sources: {all_data['web_intelligence']['total_results']} articles

Create a client-ready report with these sections:
1. EXECUTIVE SUMMARY (2-3 paragraphs)
2. KEY FINDINGS (5-7 bullet points)
3. PLATFORM INSIGHTS
   - Twitter/X Analysis
   - TikTok Analysis
   - Reddit Analysis
   - Google Trends Analysis
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
                    {"role": "system", "content": agent["system_prompt"]},
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
st.markdown("### Multi-Source Intelligence for Marketing Agencies")

st.markdown("""
This demo showcases a sophisticated multi-agent system that:
- 🔄 **Collects data** from 5 platforms in parallel
- 🔍 **Analyzes patterns** across multiple sources
- 📄 **Generates reports** ready for clients
- 🎯 **Provides insights** for marketing strategies
""")

# Configuration check
client = get_azure_client()
model = os.getenv("AZURE_AI_MODEL_NAME", "gpt-4")

if not client:
    st.error("⚠️ Please configure your Azure AI credentials in the .env file")
    st.info("See .env.example for the required format")
    st.stop()

st.success(f"✅ Connected to Azure AI | Model: {model}")

# Sidebar: Agent Team
with st.sidebar:
    st.header("🤖 Research Team")
    
    st.markdown("### Phase 1: Data Collection (Parallel)")
    for agent_key in ["social_media", "trends", "web_intelligence"]:
        agent = AGENTS[agent_key]
        st.markdown(f"""
        <div style="background-color: {agent['color']}20; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{agent['icon']} {agent['name']}</strong><br>
            <small>{agent['role'].replace('_', ' ').title()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Phase 2: Analysis & Synthesis (Sequential)")
    for agent_key in ["insight_analyst", "report_generator"]:
        agent = AGENTS[agent_key]
        st.markdown(f"""
        <div style="background-color: {agent['color']}20; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{agent['icon']} {agent['name']}</strong><br>
            <small>{agent['role'].replace('_', ' ').title()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Total Agents:** 6 (5 active + 1 orchestrator)")
    st.markdown("**Data Sources:** 5 platforms")
    st.markdown("**Execution:** Parallel → Sequential")

# Main content
st.markdown("---")
st.header("📋 Select Research Question")

# Research question selection
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

# Display question details
with st.expander("📄 Question Details", expanded=True):
    st.markdown(f"**Research Question:**")
    st.info(selected_question["question"])
    st.markdown(f"**Focus Areas:** {selected_question['focus']}")
    st.markdown(f"**Search Terms:** {', '.join(selected_question['search_terms'])}")

# Quick start buttons
col1, col2 = st.columns([1, 3])
with col1:
    start_research = st.button("🚀 Start Research", type="primary", use_container_width=True)

if start_research:
    st.markdown("---")
    st.header("🔬 Research in Progress")
    
    # Initialize APIs
    apis = get_mock_apis()
    
    # Store start time
    start_time = time.time()
    
    # Phase 1: Parallel Data Collection
    st.subheader("📊 Phase 1: Data Collection (Parallel Execution)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📱 Social Media")
        social_media_data = collect_social_media_data(selected_question, apis)
    
    with col2:
        st.markdown("#### 📈 Trends")
        trends_data = collect_trends_data(selected_question, apis)
    
    with col3:
        st.markdown("#### 🌐 Web Intelligence")
        web_intelligence_data = collect_web_intelligence(selected_question, apis)
    
    # Combine all data
    all_data = {
        "social_media": social_media_data,
        "trends": trends_data,
        "web_intelligence": web_intelligence_data
    }
    
    st.success("✅ Phase 1 Complete: All data collected")
    
    # Phase 2: Sequential Analysis & Synthesis
    st.markdown("---")
    st.subheader("🔍 Phase 2: Analysis & Synthesis (Sequential Execution)")
    
    # Step 1: Analyze insights
    insights = analyze_insights(client, model, all_data, selected_question)
    
    if insights:
        # Step 2: Generate report
        report = generate_report(client, model, all_data, insights, selected_question)
        
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
                st.metric("Data Sources", "5 platforms")
            with col2:
                total_data_points = (
                    social_media_data["twitter"]["total_results"] +
                    social_media_data["tiktok"]["total_results"] +
                    social_media_data["reddit"]["total_results"] +
                    web_intelligence_data["total_results"]
                )
                st.metric("Data Points", f"{total_data_points:,}")
            with col3:
                st.metric("Execution Time", f"{execution_time:.1f}s")
            with col4:
                st.metric("Agents Used", "5")
            with col5:
                st.metric("Report Sections", "7")
            
            # Display report
            st.markdown(report)
            
            # Download options
            st.markdown("---")
            st.subheader("💾 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                export_data = {
                    "question": selected_question["question"],
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "data_sources": {
                        "twitter": social_media_data["twitter"],
                        "tiktok": social_media_data["tiktok"],
                        "reddit": social_media_data["reddit"],
                        "google_trends": trends_data,
                        "web_search": web_intelligence_data
                    },
                    "insights": insights,
                    "report": report
                }
                
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📥 Download Full Data (JSON)",
                    data=json_str,
                    file_name=f"research_report_{selected_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Text report export
                report_text = f"""
MARKETING RESEARCH REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESEARCH QUESTION:
{selected_question['question']}

{report}

---
Data Sources: Twitter/X, TikTok, Reddit, Google Trends, Web Search
Total Data Points: {total_data_points:,}
Execution Time: {execution_time:.1f} seconds
"""
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=report_text,
                    file_name=f"research_report_{selected_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("---")
st.markdown("""
### 🎯 What This Demo Shows

**Agentic Patterns:**
- ✅ **Parallel Execution** - Multiple agents collecting data simultaneously
- ✅ **Sequential Processing** - Ordered analysis and synthesis
- ✅ **Multi-Source Aggregation** - Combining data from 5 platforms
- ✅ **Complex Orchestration** - Coordinating 6 specialized agents

**Real-World Application:**
Marketing agencies can use this pattern to:
- Conduct comprehensive market research
- Analyze social media trends
- Generate client-ready reports
- Make data-driven recommendations

**Production Considerations:**
- Replace mock APIs with real API connectors
- Add caching for expensive API calls
- Implement rate limiting and error handling
- Add data validation and quality checks
- Store results in database for historical analysis
""")
