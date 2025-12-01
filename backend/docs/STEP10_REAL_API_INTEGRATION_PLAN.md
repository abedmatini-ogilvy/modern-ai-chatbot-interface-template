# Step 10: Real API Integration Plan

> **Status**: 📋 Planning Complete  
> **Last Updated**: November 2024  
> **Approach**: Incremental (one API at a time)

## 📋 Overview

This document outlines the plan to replace mock data connectors with real API integrations for the 6 specialized research agents.

### Goals
- ✅ Connect to real data sources (Twitter, Reddit, TikTok, Google Trends, Web Search)
- ✅ Implement real LLM analysis (starting with Google Gemini)
- ✅ Maintain fallback to mock data when APIs fail
- ✅ Transparent error handling with clear user messaging
- ✅ Modular architecture for easy maintenance and testing

### Key Decisions
| Decision | Choice |
|----------|--------|
| Implementation Order | Twitter → Reddit → Google Trends → Web Search → TikTok → LLM |
| API Tiers | Free tiers first |
| Error Handling | Transparent - show which API failed, continue with available data |
| Caching | In-memory caching now, database later |
| First LLM | Google Gemini |
| Frontend LLM Selection | Simple dropdown before starting research |
| Testing | Individual test script per connector |
| Environment | Codespaces first, then staging |

---

## 🏗️ Architecture Overview

### Current State (Mock)
```
research_service.py → api_connectors_mock.py → Returns fake data
```

### Target State (Real + Fallback)
```
research_service.py 
    ↓
connectors/
    ├── twitter_connector.py    → Twitter API (free) + Nitter fallback
    ├── reddit_connector.py     → Reddit API (PRAW)
    ├── google_trends_connector.py → pytrends + Google Trends API
    ├── web_search_connector.py → SerpAPI + Brave Search
    ├── tiktok_connector.py     → TikTok Creative Center API
    └── llm_connector.py        → Gemini → Azure OpenAI → others
    ↓
api_connectors_mock.py (fallback when real APIs fail)
```

### New Directory Structure
```
backend/
├── connectors/                    # NEW - Modular API connectors
│   ├── __init__.py               # Exports all connectors
│   ├── base_connector.py         # Abstract base class
│   ├── twitter_connector.py      # Twitter/X + Nitter
│   ├── reddit_connector.py       # Reddit via PRAW
│   ├── tiktok_connector.py       # TikTok Creative Center
│   ├── google_trends_connector.py # pytrends + API
│   ├── web_search_connector.py   # SerpAPI + Brave
│   ├── llm_connector.py          # Multi-provider LLM
│   └── tests/                    # Connector tests
│       ├── __init__.py
│       ├── test_twitter.py
│       ├── test_reddit.py
│       ├── test_google_trends.py
│       ├── test_web_search.py
│       ├── test_tiktok.py
│       └── test_llm.py
├── api_connectors_mock.py        # KEEP - fallback data
├── api_connectors_real.py        # UPDATE - imports from connectors/
└── ...
```

---

## 📅 Implementation Phases

### Phase 1: Foundation (Day 1)
**Goal**: Set up modular connector architecture

- [ ] Create `connectors/` directory structure
- [ ] Implement `base_connector.py` with abstract interface
- [ ] Create connector factory pattern
- [ ] Set up environment variable templates
- [ ] Update `requirements.txt` with new dependencies

**Deliverables**:
- `connectors/__init__.py`
- `connectors/base_connector.py`
- `.env.template` updated

---

### Phase 2: Twitter/X API (Days 2-3)
**Goal**: Real Twitter data with graceful fallback

#### 2.1 Twitter API v2 (Free Tier)
- [ ] Set up Twitter Developer account
- [ ] Implement `twitter_connector.py`
- [ ] Handle rate limits (1,500 tweets/month)
- [ ] Parse tweet data (text, engagement, date, author)
- [ ] Create `test_twitter.py`

#### 2.2 Nitter Fallback (Experimental)
- [ ] Research Nitter instances
- [ ] Implement scraping logic
- [ ] Add as fallback when Twitter API exhausted
- [ ] Handle Nitter instance failures

**Free Tier Limits**:
- 1,500 tweets/month READ
- ~50 tweets per research session
- Rate limit: 1 request/second

**Error Messages**:
```
"Twitter API quota exhausted. Using cached data."
"Twitter API unavailable. Continuing with other sources."
```

---

### Phase 3: Reddit API (Days 4-5)
**Goal**: Rich discussion data from subreddits

- [ ] Create Reddit app (script type)
- [ ] Implement `reddit_connector.py` using PRAW
- [ ] Search posts and comments
- [ ] Extract: title, body, score, comments, subreddit
- [ ] Create `test_reddit.py`

**Free Tier Limits**:
- 60 requests/minute
- 100 requests with OAuth
- Very generous for MVP

**Target Data**:
- 50-100 posts per research
- Top comments per post
- Subreddit metadata

---

### Phase 4: Google Trends (Days 6-7)
**Goal**: Search trend data and related queries

#### 4.1 pytrends (No API Key)
- [ ] Implement using `pytrends` library
- [ ] Get interest over time
- [ ] Get related queries
- [ ] Get regional interest
- [ ] Handle rate limiting

#### 4.2 Google Trends API (Backup)
- [ ] Research official API access
- [ ] Implement as backup if pytrends blocked
- [ ] Compare results between methods

**No API Key Required** for pytrends (unofficial)

**Target Data**:
- Interest over time (90 days)
- Related queries (top 25)
- Rising queries
- Regional breakdown

---

### Phase 5: Web Search (Days 8-10)
**Goal**: Multiple search engine support

#### 5.1 SerpAPI (Primary)
- [ ] Create SerpAPI account
- [ ] Implement Google search results
- [ ] Parse snippets, titles, URLs
- [ ] Create `test_web_search.py`

#### 5.2 Brave Search API (Backup)
- [ ] Create Brave Search account
- [ ] Implement as secondary source
- [ ] Compare result quality

**Free Tier Limits**:
| Service | Free Limit |
|---------|------------|
| SerpAPI | 100/month |
| Brave Search | 2,000/month |

**Target Data**:
- 20-50 search results
- Title, snippet, URL
- Date when available

---

### Phase 6: TikTok (Days 11-12)
**Goal**: TikTok trends and content data

- [ ] Research TikTok Creative Center API
- [ ] Apply for access if needed
- [ ] Implement `tiktok_connector.py`
- [ ] Focus on trending topics and hashtags
- [ ] Create `test_tiktok.py`

**Note**: TikTok API access is limited. May need to:
- Use Creative Center (trends only)
- Skip for MVP if access denied
- Use mock data as fallback

**Target Data**:
- Trending hashtags
- Popular sounds
- Creator trends
- Engagement metrics (if available)

---

### Phase 7: LLM Integration (Days 13-16)
**Goal**: Real AI-powered analysis

#### 7.1 Google Gemini (Primary)
- [ ] Set up Google AI Studio account
- [ ] Get Gemini API key
- [ ] Implement `llm_connector.py`
- [ ] Create analysis prompts
- [ ] Create report generation prompts

#### 7.2 Multi-Provider Architecture
- [ ] Abstract LLM interface
- [ ] Add Azure OpenAI support
- [ ] Add configuration for model selection
- [ ] Frontend dropdown for LLM choice

**Free Tier Limits**:
| Provider | Free Limit |
|----------|------------|
| Gemini | 60 requests/min, 1M tokens/day |
| Azure OpenAI | Pay-as-you-go (~$0.01-0.03/1K tokens) |

**LLM Tasks**:
1. Summarize collected data
2. Extract key insights
3. Generate recommendations
4. Create executive summary

---

### Phase 8: Integration & Testing (Days 17-19)
**Goal**: End-to-end testing and optimization

- [ ] Integration tests for full research flow
- [ ] Error handling validation
- [ ] Caching implementation
- [ ] Performance benchmarks
- [ ] Documentation updates

---

### Phase 9: Frontend Updates (Day 20)
**Goal**: LLM selection UI

- [ ] Add LLM selector dropdown
- [ ] Display which APIs were used
- [ ] Show API status/errors in UI
- [ ] Update result display for real data

---

## 📦 Dependencies to Add

```txt
# requirements.txt additions

# Twitter
tweepy>=4.14.0

# Reddit  
praw>=7.7.0

# Google Trends
pytrends>=4.9.0

# Web Search
google-search-results>=2.4.2  # SerpAPI
requests>=2.31.0  # For Brave Search

# TikTok (if available)
# TBD based on API access

# LLM Providers
google-generativeai>=0.3.0  # Gemini
openai>=1.0.0  # Azure OpenAI
anthropic>=0.7.0  # Claude (future)

# Caching
cachetools>=5.3.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
python-dotenv>=1.0.0
```

---

## 🔑 Environment Variables Template

```bash
# .env.template

# ===================
# Twitter/X API
# ===================
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# ===================
# Reddit API
# ===================
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=TrendResearchBot/1.0

# ===================
# Web Search
# ===================
SERPAPI_API_KEY=
BRAVE_SEARCH_API_KEY=

# ===================
# TikTok (if available)
# ===================
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=

# ===================
# LLM Providers
# ===================
# Google Gemini
GOOGLE_AI_API_KEY=

# Azure OpenAI
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT_NAME=

# ===================
# Configuration
# ===================
# Default LLM provider: gemini, azure, anthropic
DEFAULT_LLM_PROVIDER=gemini

# Enable/disable specific connectors
ENABLE_TWITTER=true
ENABLE_REDDIT=true
ENABLE_GOOGLE_TRENDS=true
ENABLE_WEB_SEARCH=true
ENABLE_TIKTOK=true

# Use mock data as fallback
ENABLE_MOCK_FALLBACK=true

# Cache settings
CACHE_TTL_SECONDS=3600
```

---

## ✅ Success Criteria

### Per Connector
- [ ] Returns real data from API
- [ ] Handles rate limits gracefully
- [ ] Falls back to mock data on failure
- [ ] Provides clear error messages
- [ ] Passes all unit tests
- [ ] Logs API usage for monitoring

### Overall System
- [ ] Complete research in <30 seconds
- [ ] At least 3/5 APIs returning real data
- [ ] LLM generates coherent analysis
- [ ] User sees which sources succeeded/failed
- [ ] No crashes on API failures

---

## 🚀 Quick Start for Each Phase

When starting a phase, use this command:
```bash
# Example for Phase 2 (Twitter)
cd backend
python -m pytest connectors/tests/test_twitter.py -v
```

See `API_SETUP_GUIDES.md` for credential setup instructions.
See `API_CONNECTORS_ARCHITECTURE.md` for implementation details.

---

## 📊 Progress Tracker

| Phase | Component | Status | Notes |
|-------|-----------|--------|-------|
| 1 | Foundation | ⬜ Not Started | |
| 2 | Twitter/X | ⬜ Not Started | |
| 3 | Reddit | ⬜ Not Started | |
| 4 | Google Trends | ⬜ Not Started | |
| 5 | Web Search | ⬜ Not Started | |
| 6 | TikTok | ⬜ Not Started | |
| 7 | LLM Integration | ⬜ Not Started | |
| 8 | Testing | ⬜ Not Started | |
| 9 | Frontend | ⬜ Not Started | |

**Legend**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Blocked

---

## 📝 Notes & Decisions Log

### November 2024
- Decided on incremental approach
- Twitter free tier + Nitter experimental
- Starting with Gemini for LLM
- Modular connector architecture approved
- Focus on free tiers for MVP
