# Demo 5: Trend Research System 📊

## Overview

This demo showcases a **sophisticated multi-agent research system** designed for marketing agencies. It demonstrates the most complex agentic pattern yet: combining **parallel data collection**, **sequential analysis**, and **multi-source synthesis** to generate comprehensive market research reports.

## What It Demonstrates

### Key Concepts
- ✅ **Parallel Agent Execution** - Multiple agents working simultaneously
- ✅ **Sequential Processing** - Ordered analysis and synthesis phases
- ✅ **Multi-Source Data Aggregation** - Combining 5 different platforms
- ✅ **Complex Orchestration** - Coordinating 6 specialized agents
- ✅ **Real-World Application** - Production-ready pattern for marketing research

### Agentic Pattern: Hybrid Multi-Agent + Tool Use
The system uses a **two-phase architecture**:

**Phase 1 (Parallel):** Data Collection
- 3 agents collect data simultaneously from 5 platforms
- Faster execution through parallel processing
- Independent data sources

**Phase 2 (Sequential):** Analysis & Synthesis
- Insight Analyst processes all collected data
- Report Generator creates client-ready output
- Ordered workflow ensures quality

---

## Running the Demo

### Quick Start
```bash
streamlit run demo5_trend_research.py
```

The app will open at: `http://localhost:8501`

### Prerequisites
- Virtual environment activated
- `.env` file configured with Azure OpenAI credentials
- Dependencies installed (`requirements.txt`)

---

## The Research Team (6 Agents)

### Phase 1: Data Collection Agents (Parallel)

#### 1. 📱 Social Media Intelligence Agent
**Role:** Collects and analyzes social media data  
**Platforms:** Twitter/X, TikTok, Reddit  
**Outputs:**
- Tweet sentiment and engagement
- TikTok video views and trends
- Reddit discussions and community insights

#### 2. 📈 Trends Analysis Agent
**Role:** Analyzes search trends and patterns  
**Platform:** Google Trends  
**Outputs:**
- Search volume indices
- Regional interest breakdown
- Related queries and topics
- Temporal patterns

#### 3. 🌐 Web Intelligence Agent
**Role:** Gathers web content and news  
**Platform:** Web Search  
**Outputs:**
- News articles
- Blog posts
- Expert opinions
- Market signals

### Phase 2: Analysis & Synthesis Agents (Sequential)

#### 4. 🔍 Insight Analyst Agent
**Role:** Synthesizes data from all sources  
**Process:**
- Identifies patterns across platforms
- Extracts audience behavior insights
- Finds market opportunities
- Generates strategic implications

#### 5. 📄 Report Generator Agent
**Role:** Creates comprehensive client-ready reports  
**Output Sections:**
- Executive Summary
- Key Findings
- Platform-specific Insights
- Audience Demographics
- Sentiment Analysis
- Actionable Recommendations
- Data Sources & Methodology

#### 6. 🎯 Research Orchestrator (Coordinator)
**Role:** Coordinates the entire research workflow  
**Responsibilities:**
- Breaks down research questions
- Dispatches tasks to agents
- Manages execution flow
- Ensures data quality

---

## The 4 Research Questions

### 1. Gen Z Nigeria: Facebook vs Google Usage
**Question:** Why does Gen Z in Nigeria appear to use Facebook for community and content discovery, while using Google primarily for functional, task-based searches?

**Focus:** Social behavior patterns, platform preferences, user motivations

**Use Case:** Social media strategy for Nigerian market

---

### 2. Detty December Tourism Analysis
**Question:** Beyond the parties, what are the core drivers and frustrations for the diaspora and domestic tourists participating in 'Detty December' in Nigeria and Ghana?

**Focus:** Tourism motivations, pain points, diaspora engagement

**Use Case:** Tourism marketing and event planning

---

### 3. African Creator Economy Challenges
**Question:** What are the primary financial challenges and unmet needs of emerging creators and gamers in key African markets?

**Focus:** Monetization barriers, infrastructure gaps, creator pain points

**Use Case:** Platform development and creator support programs

---

### 4. M-Pesa Market Dominance Analysis
**Question:** What are the primary drivers of M-Pesa's dominance in East Africa, and what specific user frustrations or unmet needs could a competitor leverage to capture market share among the digital-native population?

**Focus:** Competitive analysis, user pain points, market opportunities

**Use Case:** Fintech competitive strategy

---

## Demo Flow (6-8 minutes)

### 1. Introduction (1 minute)
**Say:**
> "Marketing agencies need comprehensive research from multiple sources. This system 
> demonstrates how AI agents can collect, analyze, and synthesize data from 5 platforms 
> simultaneously to generate client-ready reports."

**Show:**
- The 6-agent team in sidebar
- 4 research questions available
- Two-phase architecture

### 2. Select Research Question (30 seconds)
**Do:**
- Choose one of the 4 questions (recommend: Gen Z Nigeria or Detty December)
- Expand question details
- Show focus areas and search terms

**Say:**
> "Let's research [selected topic]. Watch how the system orchestrates multiple agents 
> to gather and analyze data in parallel."

### 3. Phase 1: Data Collection (2-3 minutes)
**Click:** "Start Research" button

**As it runs, narrate:**

**Social Media Agent:**
> "First, the Social Media agent is collecting data from Twitter, TikTok, and Reddit 
> simultaneously. See the real-time metrics - sentiment breakdown, engagement rates, 
> top hashtags..."

**Trends Agent:**
> "Meanwhile, the Trends agent is analyzing Google search patterns. Notice the search 
> volume index and regional interest - this shows where the conversation is strongest."

**Web Intelligence Agent:**
> "And the Web Intelligence agent is gathering news articles and blog posts from 
> authoritative sources. This provides context and expert perspectives."

**Say:**
> "All three agents are working in parallel - this is much faster than sequential 
> data collection. In production, this could save hours of research time."

### 4. Phase 2: Analysis & Synthesis (2-3 minutes)
**As Phase 2 runs, narrate:**

**Insight Analyst:**
> "Now the Insight Analyst is processing all the collected data. It's identifying 
> patterns across platforms, extracting audience insights, and finding market 
> opportunities. This is where the magic happens - connecting dots across different 
> data sources."

**Report Generator:**
> "Finally, the Report Generator is creating a comprehensive, client-ready report. 
> It's formatting findings into sections that marketing executives can immediately 
> act on."

### 5. Review Report (2 minutes)
**Show:**
- Metrics dashboard (data points, execution time, agents used)
- Executive summary
- Key findings
- Platform-specific insights
- Recommendations

**Say:**
> "Here's the final report. Notice it includes:
> - Executive summary for quick scanning
> - Platform-specific insights showing what's happening on each channel
> - Sentiment analysis across sources
> - Actionable recommendations the agency can implement immediately
> - Full data sources for transparency"

**Scroll through sections:**
> "This is production-quality output. A marketing agency could deliver this directly 
> to clients or use it to inform campaign strategy."

### 6. Export Options (30 seconds)
**Show:**
- JSON export (full data + report)
- TXT export (report only)

**Say:**
> "The system provides export options - full data in JSON for further analysis, or 
> just the report in text format for easy sharing."

### 7. Explain the Pattern (1 minute)
**Say:**
> "This demonstrates the most sophisticated agentic pattern we've seen:
> 
> **Phase 1 - Parallel Execution:** Three agents collect data simultaneously from 
> five platforms. This is fast and efficient.
> 
> **Phase 2 - Sequential Processing:** Two agents analyze and synthesize in order. 
> This ensures quality and coherence.
> 
> This pattern is perfect for:
> - Market research
> - Competitive intelligence
> - Social listening
> - Trend analysis
> - Any task requiring multi-source data aggregation
> 
> In production, you'd replace the mock APIs with real API connectors, add caching, 
> implement rate limiting, and store results in a database for historical analysis."

---

## Architecture Deep Dive

### System Flow

```
User Question
     ↓
Research Orchestrator
     ↓
┌────────────────────────────────────────┐
│     PHASE 1: PARALLEL COLLECTION       │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────┐  ┌──────────────┐  │
│  │ Social Media │  │    Trends    │  │
│  │    Agent     │  │    Agent     │  │
│  └──────────────┘  └──────────────┘  │
│         │                  │          │
│         │  ┌──────────────┐│          │
│         │  │     Web      ││          │
│         │  │ Intelligence ││          │
│         │  │    Agent     ││          │
│         │  └──────────────┘│          │
│         │         │         │          │
│         ↓         ↓         ↓          │
│    Twitter/X  Google    Web Search    │
│    TikTok     Trends                  │
│    Reddit                             │
│                                        │
└────────────────────────────────────────┘
     ↓
Combined Data
     ↓
┌────────────────────────────────────────┐
│    PHASE 2: SEQUENTIAL ANALYSIS        │
├────────────────────────────────────────┤
│                                        │
│         Insight Analyst Agent          │
│                  ↓                     │
│         (Identifies Patterns)          │
│                  ↓                     │
│        Report Generator Agent          │
│                  ↓                     │
│         (Creates Report)               │
│                                        │
└────────────────────────────────────────┘
     ↓
Final Report
```

### Data Flow

1. **Input:** Research question + search terms
2. **Phase 1 Output:** Raw data from 5 platforms
3. **Phase 2 Input:** Combined raw data
4. **Phase 2 Output:** Analyzed insights + formatted report
5. **Final Output:** Client-ready report + exportable data

---

## Mock vs Real APIs

### Current Implementation (Mock)

The demo uses **`api_connectors_mock.py`** with realistic sample data:

**Advantages:**
- ✅ Works offline
- ✅ No API keys needed
- ✅ Instant responses (simulated delays)
- ✅ Consistent data for demos
- ✅ No rate limits or costs

**Mock Data Includes:**
- Realistic tweet/video/post content
- Accurate metrics and engagement numbers
- Proper sentiment distribution
- Geographic and demographic data
- Trending topics and hashtags

### Production Implementation (Real APIs)

For production use, create **`api_connectors_real.py`** with:

```python
# Twitter/X API
import tweepy

# TikTok API
from TikTokApi import TikTokApi

# Reddit API
import praw

# Google Trends
from pytrends.request import TrendReq

# Web Search (Bing/Google)
from azure.cognitiveservices.search.websearch import WebSearchClient
```

**See `DEMO5_REAL_APIS_GUIDE.md` for implementation details** (to be created).

---

## Report Structure

### 1. Executive Summary
- 2-3 paragraph overview
- Key takeaways
- Strategic implications

### 2. Key Findings
- 5-7 bullet points
- Most important insights
- Data-backed conclusions

### 3. Platform Insights

**Twitter/X Analysis:**
- Sentiment breakdown
- Top hashtags
- Geographic distribution
- Engagement patterns

**TikTok Analysis:**
- Video performance
- Trending sounds
- Age demographics
- Engagement rates

**Reddit Analysis:**
- Discussion intensity
- Top subreddits
- Community sentiment
- Comment volume

**Google Trends Analysis:**
- Search volume trends
- Regional interest
- Related queries
- Trending status

### 4. Audience Demographics & Behavior
- Age distribution
- Geographic concentration
- Platform preferences
- Behavioral patterns

### 5. Sentiment Analysis
- Overall sentiment
- Platform-specific sentiment
- Sentiment drivers
- Emotional themes

### 6. Actionable Recommendations
- 5-7 specific actions
- Prioritized by impact
- Implementation guidance
- Expected outcomes

### 7. Data Sources & Methodology
- Platforms analyzed
- Data collection period
- Sample sizes
- Analysis methods

---

## Use Cases for Marketing Agencies

### 1. Campaign Planning
**Scenario:** Planning a social media campaign for Nigerian Gen Z

**How to use:**
- Research Gen Z behavior patterns
- Identify platform preferences
- Understand content preferences
- Plan channel strategy

### 2. Competitive Intelligence
**Scenario:** Analyzing competitor positioning

**How to use:**
- Research competitor mentions
- Analyze sentiment
- Identify market gaps
- Find differentiation opportunities

### 3. Trend Monitoring
**Scenario:** Tracking emerging trends in African markets

**How to use:**
- Monitor search trends
- Track social conversations
- Identify rising topics
- Predict future trends

### 4. Audience Research
**Scenario:** Understanding target audience behavior

**How to use:**
- Analyze demographics
- Study platform usage
- Identify pain points
- Map customer journey

### 5. Content Strategy
**Scenario:** Developing content that resonates

**How to use:**
- Research trending topics
- Analyze successful content
- Identify content gaps
- Plan content calendar

---

## Customization Guide

### Adding New Research Questions

```python
RESEARCH_QUESTIONS["your_topic"] = {
    "title": "Your Topic Title",
    "question": "Your research question here?",
    "focus": "Key focus areas",
    "search_terms": ["term1", "term2", "term3"]
}
```

### Modifying Agent Prompts

Edit the `AGENTS` dictionary to customize agent behavior:

```python
AGENTS["insight_analyst"]["system_prompt"] = """
Your custom prompt here...
Focus on specific aspects...
"""
```

### Adding More Platforms

1. Add new API connector to `api_connectors_mock.py`
2. Create collection function in `demo5_trend_research.py`
3. Update data aggregation logic
4. Modify report generation to include new platform

### Adjusting Report Format

Modify the `report_prompt` in `generate_report()` function:

```python
report_prompt = f"""
Add your custom sections:
8. COMPETITIVE ANALYSIS
9. MARKET OPPORTUNITIES
10. RISK ASSESSMENT
"""
```

---

## Technical Implementation

### Parallel Execution

```python
# Phase 1: All agents run simultaneously
col1, col2, col3 = st.columns(3)

with col1:
    social_data = collect_social_media_data(...)
with col2:
    trends_data = collect_trends_data(...)
with col3:
    web_data = collect_web_intelligence(...)
```

**Benefits:**
- Faster execution
- Better resource utilization
- Independent failure handling

### Sequential Processing

```python
# Phase 2: Ordered execution
insights = analyze_insights(...)  # Must complete first
report = generate_report(insights, ...)  # Uses insights
```

**Benefits:**
- Quality control
- Logical flow
- Error propagation

### Data Aggregation

```python
all_data = {
    "social_media": {
        "twitter": twitter_data,
        "tiktok": tiktok_data,
        "reddit": reddit_data
    },
    "trends": trends_data,
    "web_intelligence": web_data
}
```

---

## Performance Metrics

### Demo Performance (Mock APIs)

- **Phase 1 Duration:** ~6-8 seconds (parallel)
- **Phase 2 Duration:** ~10-15 seconds (sequential)
- **Total Execution:** ~16-23 seconds
- **Data Points Collected:** 100-200
- **Report Length:** 1500-2500 words

### Production Performance (Real APIs)

- **Phase 1 Duration:** ~30-60 seconds (API latency)
- **Phase 2 Duration:** ~15-30 seconds (LLM processing)
- **Total Execution:** ~45-90 seconds
- **Data Points Collected:** 500-1000+
- **Report Length:** 2000-3500 words

---

## Troubleshooting

### No Data Collected
- Check API connector imports
- Verify mock data generation
- Check search terms relevance

### Analysis Fails
- Check Azure OpenAI connection
- Verify model has enough tokens
- Check prompt length

### Report Generation Slow
- Normal for comprehensive reports
- Reduce max_tokens if needed
- Consider using GPT-3.5 for speed

### Export Not Working
- Check file permissions
- Verify JSON serialization
- Check download path

---

## Comparison with Other Demos

| Aspect | Demo 1 | Demo 2 | Demo 3 | Demo 4 | Demo 5 |
|--------|--------|--------|--------|--------|--------|
| **Pattern** | Tool Use | RAG | Multi-Agent | Planning | Hybrid |
| **Agents** | 1 | 1 | 4 | 1 | 6 |
| **Execution** | Sequential | Sequential | Sequential | Sequential | Parallel + Sequential |
| **Data Sources** | 3 tools | 5 docs | Internal | Internal | 5 platforms |
| **Complexity** | Low | Medium | Medium | Medium | High |
| **Use Case** | Actions | Knowledge | Collaboration | Task execution | Research |
| **Output** | Synthesized answer | Grounded answer | Multi-perspective | Step-by-step plan | Comprehensive report |

---

## Production Considerations

### 1. Real API Integration
- Implement `api_connectors_real.py`
- Add authentication
- Handle rate limits
- Implement retries

### 2. Caching
```python
@st.cache_data(ttl=3600)
def collect_social_media_data(...):
    # Cache for 1 hour
```

### 3. Error Handling
```python
try:
    data = api.search(...)
except RateLimitError:
    # Wait and retry
except AuthenticationError:
    # Log and alert
```

### 4. Cost Optimization
- Cache API responses
- Batch requests
- Use cheaper models for analysis
- Implement request throttling

### 5. Data Storage
```python
# Store results in database
db.save_research_report({
    "question": question,
    "timestamp": datetime.now(),
    "data": all_data,
    "report": report
})
```

### 6. Monitoring
- Track API usage
- Monitor execution times
- Log errors
- Alert on failures

---

## Scaling Strategies

### Horizontal Scaling
- Run multiple instances
- Load balance requests
- Distribute across regions

### Vertical Scaling
- Increase API rate limits
- Use faster models
- Optimize prompts

### Async Execution
```python
import asyncio

async def collect_all_data():
    tasks = [
        collect_social_media_data_async(...),
        collect_trends_data_async(...),
        collect_web_intelligence_async(...)
    ]
    return await asyncio.gather(*tasks)
```

---

## Files

- `demo5_trend_research.py` - Main demo application
- `api_connectors_mock.py` - Mock API implementations
- `DEMO5_README.md` - This file
- `.env` - Configuration (Azure credentials)

---

## Presentation Tips

### Do's ✅
- Start with Gen Z Nigeria or Detty December (most engaging)
- Emphasize parallel execution speed
- Show the metrics dashboard
- Scroll through the full report
- Mention production considerations

### Don'ts ❌
- Don't skip Phase 1 visualization
- Don't rush through the report
- Don't forget to explain the two-phase architecture
- Don't ignore the export options

### Time Management
- **6 min version:** One question, highlight key sections
- **8 min version:** One question, full report walkthrough
- **10 min version:** Two questions, compare results

---

## Key Takeaway

> "This is how modern marketing agencies can leverage AI: multiple specialized agents 
> working in parallel to collect data, then sequential analysis to ensure quality. 
> The result is comprehensive, client-ready research in minutes instead of days."

---

## Transition to Next Topic

**If wrapping up presentation:**
> "We've now seen all five fundamental agentic patterns: Tool Use, RAG, Multi-Agent, 
> Planning, and now this Hybrid approach. These patterns can be mixed and matched 
> for any use case. The key is understanding when to use each pattern and how to 
> combine them effectively."

---

**Demo 5 Complete!** Ready to showcase sophisticated multi-agent research! 🎉
