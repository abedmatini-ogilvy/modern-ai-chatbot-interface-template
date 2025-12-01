# AI-Powered Trend Research System

A modern full-stack application that conducts multi-agent marketing research with real-time progress tracking and comprehensive report generation.

[![Built with v0](https://img.shields.io/badge/Built%20with-v0.app-black?style=for-the-badge)](https://v0.app/chat/NsuTJm7wr0L)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/abedmatini-6352s-projects/v0-modern-ai-chatbot-interface-tem-fy)

## 🎯 Mission

Transform marketing research by automating multi-source data collection and AI-powered analysis. This system enables marketing teams to:

- **Conduct comprehensive trend research** across social media, search trends, and web sources
- **Get actionable insights** with AI-powered analysis and recommendations
- **Track research progress** in real-time through an intuitive chat interface
- **Scale research operations** with concurrent session support and efficient data collection

## ✨ Features

### Multi-Agent Research System
- **6 Specialized Agents**: Twitter, TikTok, Reddit, Google Trends, Web Search, Analyst
- **Parallel Data Collection**: Gathers 150+ data points in ~10 seconds
- **AI-Powered Analysis**: Synthesizes insights from multiple sources
- **Structured Reports**: Executive summaries, key findings, and actionable recommendations

### Modern Chat Interface
- **Real-time Progress Updates**: Live status messages as agents work
- **Multi-message Results**: Organized display of research findings
- **Concurrent Sessions**: Run multiple research queries simultaneously
- **Research Questions Library**: Pre-configured trending topics

### Technical Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Python asyncio, Pydantic validation
- **Architecture**: REST API with polling, in-memory session management
- **AI Integration**: Google Gemini 2.0 Flash (primary), Azure OpenAI (fallback)
- **Real APIs**: Twitter, Reddit, Google Trends, SerpAPI Web Search

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.8+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/abedmatini-ogilvy/modern-ai-chatbot-interface-template.git
cd modern-ai-chatbot-interface-template
```

### 2. Start the Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 3. Start the Frontend (Next.js)

```bash
# From project root
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:3000`
- Main Chat: `http://localhost:3000`
- API Test Page: `http://localhost:3000/api-test`

### 4. Test the Integration

1. Open `http://localhost:3000` in your browser
2. Click the hamburger menu (☰) on the left
3. Under "RESEARCH QUESTIONS", click any research topic
4. Watch progress messages appear in real-time
5. Review the complete research report (~10-12 seconds)

## ✅ What's Been Completed

### Backend (100%)
- ✅ FastAPI application structure with CORS
- ✅ 7 REST API endpoints (start, status, result, questions, sessions, delete, statistics)
- ✅ Multi-agent research orchestration
- ✅ Session management with automatic cleanup (60min timeout)
- ✅ Real API connectors (Twitter, Reddit, Google Trends, Web Search)
- ✅ AI-powered analysis with Google Gemini 2.0 Flash
- ✅ Progress tracking with 18+ status updates per research
- ✅ Graceful error handling and fallbacks to mock data

### Frontend (100%)
- ✅ TypeScript API client with full type safety (540 lines)
- ✅ React hooks for state management (260 lines)
- ✅ Chat interface integration with real-time updates
- ✅ Multi-message result display (summary, findings, recommendations)
- ✅ Research questions loaded from API
- ✅ Concurrent session support
- ✅ Progress message rendering
- ✅ API test page for debugging

### Documentation (100%)
- ✅ API reference guide
- ✅ Architecture diagrams
- ✅ Step-by-step implementation logs
- ✅ Testing documentation

## 🔄 What's Left (Optional Enhancements)

### Step 10: Real API Integration ✅ COMPLETE
- ✅ Google Gemini 2.0 Flash for AI-powered analysis
- ✅ Twitter API (tweepy) - working with rate limit handling
- ✅ Reddit API (praw) - fully functional
- ✅ Google Trends (pytrends) - FREE, no API key needed!
- ✅ SerpAPI Web Search - working
- ⚠️ TikTok API - requires Creative Center approval (falls back to mock)
- ✅ Modular connector architecture with graceful degradation
- ✅ `.env.template` setup guide created

### Future Enhancements
- [ ] Frontend LLM selector dropdown (choose Gemini/Azure/Ollama)
- [ ] Database persistence (PostgreSQL/Redis)
- [ ] User authentication and authorization
- [ ] Download reports (PDF/Markdown)
- [ ] Research history and favorites
- [ ] Custom research question builder
- [ ] Advanced filtering and search
- [ ] Analytics dashboard
- [ ] Production deployment guide

## 📁 Project Structure

```
.
├── app/                      # Next.js app directory
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   └── api-test/            # API testing page
├── backend/                  # FastAPI backend
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── requirements.txt     # Python dependencies
│   ├── api_connectors_mock.py   # Mock data fallbacks
│   ├── api_connectors_real.py   # Real API adapter layer
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   ├── connectors/          # Modular API connectors
│   │   ├── base_connector.py       # Abstract base class
│   │   ├── twitter_connector.py    # Twitter/X API
│   │   ├── reddit_connector.py     # Reddit via PRAW
│   │   ├── google_trends_connector.py  # pytrends (FREE)
│   │   ├── web_search_connector.py # SerpAPI + fallbacks
│   │   ├── tiktok_connector.py     # TikTok Creative Center
│   │   ├── llm_connector.py        # Multi-provider LLM
│   │   └── tests/           # Connector unit tests
│   └── docs/                # Documentation
├── components/               # React components
│   ├── AIAssistantUI.jsx    # Main chat interface
│   ├── ChatPane.jsx         # Message display
│   ├── Sidebar.jsx          # Navigation sidebar
│   └── ui/                  # Reusable UI components
└── lib/                      # Utilities and hooks
    ├── api-client.ts        # API client functions
    └── use-research.ts      # React hooks
```

## 🔧 Configuration

### Environment Variables

#### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (`.env` - copy from `.env.template`)
```bash
# ===================
# LLM Providers (Primary: Gemini)
# ===================
GOOGLE_AI_API_KEY=your-gemini-api-key

# Azure OpenAI (fallback)
AZURE_AI_API_KEY=your-key-here
AZURE_AI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_MODEL_NAME=gpt-4

# ===================
# Social Media APIs
# ===================
# Twitter/X API
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_SECRET=your-access-secret

# Reddit API
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=TrendResearchBot/1.0

# ===================
# Web Search
# ===================
SERPAPI_API_KEY=your-serpapi-key

# ===================
# Server Configuration
# ===================
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Session Management
SESSION_TIMEOUT_MINUTES=60
MAX_CONCURRENT_SESSIONS=100
```

### API Free Tier Limits

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Google Gemini | 60 req/min, 1M tokens/day | Primary LLM |
| Google Trends | **Unlimited** | No API key needed! |
| Reddit | 60 req/min | Very generous |
| Twitter | 10K tweets/month | Rate limited |
| SerpAPI | 100 searches/month | Web search |
| TikTok | Requires approval | Falls back to mock |

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Get research questions
curl http://localhost:8000/api/research/questions

# Start a research session
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"question_id": "gen_z_nigeria"}'
```

### Test Frontend
1. Visit `http://localhost:3000/api-test`
2. Click any research question
3. Watch progress bar and activity log
4. Review final results

## 📚 API Documentation

### Key Endpoints

- `POST /api/research/start` - Start a new research session
- `GET /api/research/{session_id}/status` - Get session status
- `GET /api/research/{session_id}/result` - Get final results
- `GET /api/research/questions` - List available research questions
- `GET /api/research/sessions` - List active sessions
- `DELETE /api/research/{session_id}` - Cancel session

Full API documentation: `http://localhost:8000/docs`

## 🎨 Customization

### Add Custom Research Questions

Edit `backend/services/research_service.py`:

```python
{
    "id": "custom_topic",
    "title": "Your Topic Title",
    "question": "Your research question?",
    "focus": "What to focus on",
    "search_terms": ["keyword1", "keyword2"]
}
```

### Modify Mock Data

Edit `backend/api_connectors_mock.py` to customize sample data responses.

## 🤝 Contributing

This project was built collaboratively and is open for enhancements. Key areas for contribution:
- Real API integrations
- Database implementations
- UI/UX improvements
- Additional research agents
- Export formats

## 📄 License

This project is part of a learning exercise and demo application.

## 🔗 Links

- **Live Demo**: [Vercel Deployment](https://vercel.com/abedmatini-6352s-projects/v0-modern-ai-chatbot-interface-tem-fy)
- **v0.app Project**: [Continue Building](https://v0.app/chat/NsuTJm7wr0L)
- **API Documentation**: `http://localhost:8000/docs` (when running locally)

## 🙏 Acknowledgments

- Built with [v0.app](https://v0.app) for initial UI design
- Frontend template from modern AI chatbot interface
- Backend architecture inspired by multi-agent AI systems
- Mock data simulates real-world API responses for testing

---

**Status**: ✅ Core functionality complete with real API integration  
**Current Version**: v1.1.0 (Real APIs + Gemini AI)  
**Completed**: Step 10 Real API Integration
