# AI Research Assistant - Future Roadmap

This document outlines planned features and improvements for future development.

---

## 📰 Phase 1: Additional News APIs

Add more data sources to improve research coverage and reliability.

### News APIs to Integrate:
- [ ] **NewsAPI.org** - https://newsapi.org/pricing
  - Free tier: 100 requests/day
  - Good coverage of news articles worldwide
  
- [ ] **NewsData.io** - https://newsdata.io/pricing
  - Free tier: 200 requests/day
  - Supports multiple languages and countries

- [ ] **GNews API** - https://gnews.io/
  - Free tier: 100 requests/day
  - Simple REST API for news articles

- [ ] **MediaStack** - https://mediastack.com/
  - Free tier: 500 requests/month
  - Real-time news data from 7,500+ sources

- [ ] **The Guardian API** - https://open-platform.theguardian.com/
  - Free tier: 12 requests/second
  - High-quality journalism content

### Implementation Notes:
- Create unified news connector interface
- Add fallback logic between news APIs
- Implement rate limiting and caching
- Track which API returned each result

---

## 🗄️ Phase 2: Database Integration

Store API calls, research results, and summaries for future retrieval and analysis.

### Database Setup:
- [ ] Choose database (PostgreSQL recommended for structured data)
- [ ] Set up SQLAlchemy ORM models
- [ ] Create migration system (Alembic)

### Tables to Create:
- [ ] `research_sessions` - Store research requests and metadata
- [ ] `api_calls` - Log every API call (platform, query, results count, timestamp)
- [ ] `research_reports` - Store generated reports and summaries
- [ ] `data_snapshots` - Store raw API responses for reprocessing
- [ ] `users` - User accounts (if adding auth)

### Features:
- [ ] Query history and search
- [ ] Re-run past research with updated data
- [ ] Analytics dashboard showing API usage
- [ ] Export research to PDF/CSV

---

## 🧠 Phase 3: Local RAG with ChromaDB

Implement Retrieval-Augmented Generation for smarter responses based on historical data.

### ChromaDB Setup:
- [ ] Install and configure ChromaDB
- [ ] Create embedding pipeline (use OpenAI embeddings or local model)
- [ ] Design collection structure for research data

### RAG Features:
- [ ] Index all research reports and summaries
- [ ] Index raw social media posts for context
- [ ] Semantic search across past research
- [ ] "Similar research" recommendations
- [ ] Context-aware responses using historical data

### Advanced RAG:
- [ ] Hybrid search (semantic + keyword)
- [ ] Time-weighted relevance (recent data ranked higher)
- [ ] Source citation in AI responses
- [ ] Multi-document summarization

---

## 💬 Phase 4: Persistent Chat History

Store and retrieve conversation history from database.

### Implementation:
- [ ] Create `conversations` table
- [ ] Create `messages` table (linked to conversations)
- [ ] Update chat service to persist messages
- [ ] Load conversation history on reconnect
- [ ] Support multiple conversations per user

### Features:
- [ ] Continue conversations across sessions
- [ ] Search through past conversations
- [ ] Export conversation history
- [ ] Delete/archive old conversations
- [ ] Conversation summaries for long chats

---

## 🎨 Phase 5: Enhanced Frontend Display

Improve visibility into what each API returned.

### API Results Display:
- [ ] Collapsible sections for each API's raw data
- [ ] Visual cards showing:
  - Platform icon and name
  - Status (success/failed/partial)
  - Results count
  - Key metrics (sentiment, engagement, etc.)
  - Sample content preview
  - "View all" expandable section
  
### Data Visualization:
- [ ] Sentiment pie charts per platform
- [ ] Engagement metrics bar charts
- [ ] Trend lines from Google Trends
- [ ] Word clouds from social content
- [ ] Timeline of posts/articles

### Interactive Features:
- [ ] Click to see full post/article
- [ ] Filter results by platform
- [ ] Sort by date/engagement/sentiment
- [ ] Compare data across platforms

---

## 🚀 Additional Suggestions

### Performance & Reliability:
- [ ] Redis caching for API responses
- [ ] Background job queue (Celery) for long research
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker pattern for failing APIs
- [ ] Health monitoring and alerting

### AI Enhancements:
- [ ] Multiple LLM support (Claude, GPT-4, Llama)
- [ ] Streaming responses for faster UX
- [ ] Custom prompts for different research types
- [ ] Fact-checking against multiple sources
- [ ] Auto-generate follow-up questions

### User Experience:
- [ ] Research templates (competitor analysis, brand monitoring, etc.)
- [ ] Scheduled/recurring research
- [ ] Email reports
- [ ] Shareable report links
- [ ] Dark/light mode themes

### Security & Scale:
- [ ] User authentication (OAuth/JWT)
- [ ] API key management
- [ ] Rate limiting per user
- [ ] Multi-tenant support
- [ ] Kubernetes deployment configs

### Analytics:
- [ ] Track most researched topics
- [ ] API reliability metrics
- [ ] Cost tracking per research
- [ ] User engagement analytics

---

## 📋 Priority Order (Suggested)

1. **Phase 2: Database** - Foundation for everything else
2. **Phase 4: Chat History** - Quick win, improves UX significantly  
3. **Phase 1: News APIs** - More data = better research
4. **Phase 5: Frontend Display** - Better visibility into results
5. **Phase 3: RAG** - Advanced feature, requires solid data foundation

---

## 🔧 Technical Stack Recommendations

| Component | Recommendation | Alternative |
|-----------|---------------|-------------|
| Database | PostgreSQL | SQLite (dev), MySQL |
| ORM | SQLAlchemy | Tortoise ORM |
| Migrations | Alembic | - |
| Vector DB | ChromaDB | Pinecone, Weaviate |
| Embeddings | OpenAI text-embedding-3-small | Sentence Transformers |
| Cache | Redis | In-memory |
| Job Queue | Celery + Redis | RQ, Dramatiq |
| Auth | NextAuth.js | Auth0, Clerk |

---

*Last updated: December 1, 2025*
