# Demo 5: Real APIs Setup Guide 🔧

## Overview

This guide will help you configure real API integrations for Demo 5: Trend Research System. The real version supports:

- 🐦 **Twitter/X API** - Tweet search and sentiment analysis
- 💬 **Reddit API** - Post and discussion search
- 📈 **Google Trends API** - Search trends and regional interest
- 🌐 **Bing Search API** - Web search and content discovery
- 🎵 **TikTok API** - Video search (requires special access)

---

## Prerequisites

### 1. Install Required Packages

```bash
# Activate your virtual environment first
.\venv\Scripts\activate

# Install API client libraries
pip install tweepy praw pytrends requests

# Optional: TikTok API (requires special setup)
# pip install TikTokApi
```

### 2. Update requirements.txt

Add these to your `requirements.txt`:

```
tweepy>=4.14.0
praw>=7.7.1
pytrends>=4.9.2
requests>=2.31.0
```

---

## API Configuration

### 1. Twitter/X API Setup 🐦

**Step 1: Get API Access**
1. Go to https://developer.twitter.com/
2. Sign up for a Developer Account
3. Create a new Project and App
4. Generate Bearer Token

**Step 2: Add to .env**
```bash
# Twitter/X API
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Free Tier Limits:**
- 500,000 tweets/month
- 100 requests/15 minutes
- Recent tweets only (last 7 days)

**Cost:** Free tier available, paid plans start at $100/month

**Documentation:** https://developer.twitter.com/en/docs/twitter-api

---

### 2. Reddit API Setup 💬

**Step 1: Create Reddit App**
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in details:
   - **Name:** Trend Research Bot
   - **Type:** Script
   - **Redirect URI:** http://localhost:8080
4. Note your `client_id` and `client_secret`

**Step 2: Add to .env**
```bash
# Reddit API
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=TrendResearchBot/1.0
```

**Free Tier Limits:**
- 60 requests/minute
- Unlimited searches
- Full historical data

**Cost:** Free

**Documentation:** https://www.reddit.com/dev/api/

---

### 3. Google Trends API Setup 📈

**Step 1: Install pytrends**
```bash
pip install pytrends
```

**Step 2: No API Key Needed!**
Google Trends via pytrends doesn't require authentication.

**Limits:**
- Rate limited (use delays between requests)
- No official API key needed
- May require CAPTCHA if overused

**Cost:** Free

**Documentation:** https://github.com/GeneralMills/pytrends

**Note:** If you get rate limited, add delays:
```python
import time
time.sleep(2)  # Wait 2 seconds between requests
```

---

### 4. Bing Search API Setup 🌐

**Step 1: Create Azure Account**
1. Go to https://portal.azure.com/
2. Create a new resource
3. Search for "Bing Search v7"
4. Create the resource
5. Get your API key from "Keys and Endpoint"

**Step 2: Add to .env**
```bash
# Bing Search API
BING_SEARCH_API_KEY=your_bing_api_key_here
```

**Free Tier Limits:**
- 1,000 transactions/month
- 3 transactions/second

**Cost:** 
- Free tier: 1,000 calls/month
- Paid: $3 per 1,000 transactions

**Documentation:** https://docs.microsoft.com/en-us/bing/search-apis/

**Alternative:** Use Google Custom Search API
```bash
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

---

### 5. TikTok API Setup 🎵 (Optional)

**Note:** TikTok API access is restricted and requires business approval.

**For Demo Purposes:**
- The system will skip TikTok if not configured
- Use mock data instead
- Or remove TikTok from the workflow

**If you have access:**
```bash
# TikTok API (if available)
TIKTOK_API_KEY=your_tiktok_api_key
```

**Documentation:** https://developers.tiktok.com/

---

## Complete .env File Example

```bash
# Azure OpenAI (Required)
AZURE_AI_API_KEY=your_azure_openai_api_key
AZURE_AI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_MODEL_NAME=gpt-4

# Twitter/X API
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABearerTokenHere

# Reddit API
REDDIT_CLIENT_ID=your_client_id_14chars
REDDIT_CLIENT_SECRET=your_client_secret_27chars
REDDIT_USER_AGENT=TrendResearchBot/1.0 by /u/yourusername

# Bing Search API
BING_SEARCH_API_KEY=your_bing_api_key_32chars

# Google Trends (no key needed, but can add config)
# GOOGLE_TRENDS_TIMEOUT=10

# TikTok API (optional, requires special access)
# TIKTOK_API_KEY=your_tiktok_api_key
```

---

## Testing Your Setup

### Test Individual APIs

Run the test script:

```bash
python api_connectors_real.py
```

**Expected Output:**
```
Testing Real APIs...
==================================================

📊 API Availability Status:
  Twitter/X API: ✅ Available
  TikTok API: ❌ Not configured
  Reddit API: ✅ Available
  Google Trends API: ✅ Available
  Web Search API: ✅ Available

Test Query: 'Gen Z Nigeria Facebook'
==================================================

1. Testing Twitter API...
   ✅ Found 10 tweets

2. Testing Reddit API...
   ✅ Found 10 posts

3. Testing Google Trends API...
   ✅ Search volume index: 68

4. Testing Web Search API...
   ✅ Found 10 results

==================================================
Testing complete!
```

### Test the Full Demo

```bash
streamlit run demo5_trend_research_real.py
```

---

## Troubleshooting

### Twitter API Issues

**Error: "403 Forbidden"**
- Check your Bearer Token is correct
- Verify your app has "Read" permissions
- Ensure you're on the correct API tier

**Error: "429 Too Many Requests"**
- You've hit rate limits
- Wait 15 minutes
- Reduce `max_results` parameter

**Error: "No tweets found"**
- Query might be too specific
- Try broader search terms
- Check if tweets exist for that topic

---

### Reddit API Issues

**Error: "401 Unauthorized"**
- Check `client_id` and `client_secret`
- Verify app type is "script"
- Check `user_agent` format

**Error: "429 Too Many Requests"**
- Wait 1 minute
- Reduce request frequency
- Add delays between calls

**Error: "No results"**
- Try different subreddits
- Broaden search query
- Check spelling

---

### Google Trends Issues

**Error: "429 Too Many Requests"**
- Google is rate limiting you
- Add delays: `time.sleep(5)`
- Try again later
- Use VPN if persistent

**Error: "No data available"**
- Query might be too specific
- Try broader terms
- Check geographic region
- Verify timeframe

---

### Bing Search API Issues

**Error: "401 Unauthorized"**
- Check API key is correct
- Verify key is from Bing Search v7
- Check key hasn't expired

**Error: "403 Forbidden"**
- Check your Azure subscription
- Verify resource is active
- Check quota limits

**Error: "No results"**
- Query might be too specific
- Try different search terms
- Check market parameter (`mkt`)

---

## Cost Management

### Free Tier Limits

| API | Free Tier | Paid Tier |
|-----|-----------|-----------|
| **Twitter** | 500K tweets/month | $100/month+ |
| **Reddit** | Unlimited | Free |
| **Google Trends** | Unlimited* | Free |
| **Bing Search** | 1K calls/month | $3/1K calls |
| **TikTok** | N/A | Contact TikTok |

*Rate limited, not quota limited

### Staying Within Free Limits

**Twitter:**
- Use `max_results=10-50` instead of 100
- Cache results
- Don't run repeatedly

**Bing Search:**
- Use `max_results=10-20` instead of 50
- Cache results for 24 hours
- Only search when needed

**Google Trends:**
- Add 2-5 second delays between requests
- Don't run in loops
- Cache results

---

## Production Best Practices

### 1. Implement Caching

```python
import streamlit as st
from datetime import timedelta

@st.cache_data(ttl=timedelta(hours=1))
def cached_twitter_search(query):
    return apis["twitter"].search_tweets(query)
```

### 2. Add Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=10):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def search_twitter(query):
    return apis["twitter"].search_tweets(query)
```

### 3. Implement Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def robust_api_call(api_func, *args, **kwargs):
    return api_func(*args, **kwargs)
```

### 4. Monitor API Usage

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_api_call(api_name, success, result_count=0):
    logger.info(f"{api_name}: {'✅' if success else '❌'} - {result_count} results")
```

### 5. Store Results

```python
import json
from datetime import datetime

def save_results(query, results):
    filename = f"results_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
```

---

## Switching Between Mock and Real APIs

### Option 1: Environment Variable

```python
# In demo5_trend_research_real.py
USE_REAL_APIS = os.getenv("USE_REAL_APIS", "false").lower() == "true"

if USE_REAL_APIS:
    from api_connectors_real import get_real_apis as get_apis
else:
    from api_connectors_mock import get_mock_apis as get_apis
```

```bash
# In .env
USE_REAL_APIS=true
```

### Option 2: Command Line Argument

```python
import sys

if "--real" in sys.argv:
    from api_connectors_real import get_real_apis as get_apis
else:
    from api_connectors_mock import get_mock_apis as get_apis
```

```bash
streamlit run demo5_trend_research_real.py -- --real
```

---

## API Alternatives

### If Twitter is too expensive:

**Alternative 1: Mastodon API**
- Free and open source
- Similar to Twitter
- Library: `Mastodon.py`

**Alternative 2: News API**
- Free tier: 100 requests/day
- Good for news trends
- https://newsapi.org/

### If Bing is too expensive:

**Alternative 1: Google Custom Search**
- Free tier: 100 queries/day
- https://developers.google.com/custom-search

**Alternative 2: DuckDuckGo API**
- Unofficial but free
- Library: `duckduckgo-search`

### If TikTok is unavailable:

**Alternative: YouTube API**
- Free tier: 10,000 units/day
- Good for video trends
- https://developers.google.com/youtube

---

## Security Best Practices

### 1. Never Commit API Keys

```bash
# Always in .gitignore
.env
*.key
*.secret
credentials/
```

### 2. Use Environment Variables

```python
# Good ✅
api_key = os.getenv("TWITTER_BEARER_TOKEN")

# Bad ❌
api_key = "AAAAAAAAAAAAAAAAAAAAABearerToken"
```

### 3. Rotate Keys Regularly

- Change API keys every 90 days
- Use different keys for dev/prod
- Monitor for unauthorized usage

### 4. Implement Key Validation

```python
def validate_api_keys():
    required_keys = [
        "AZURE_AI_API_KEY",
        "TWITTER_BEARER_TOKEN",
        "REDDIT_CLIENT_ID"
    ]
    
    missing = [key for key in required_keys if not os.getenv(key)]
    
    if missing:
        raise ValueError(f"Missing API keys: {', '.join(missing)}")
```

---

## Quick Start Checklist

- [ ] Install required packages (`pip install tweepy praw pytrends requests`)
- [ ] Create Twitter Developer account and get Bearer Token
- [ ] Create Reddit app and get credentials
- [ ] Create Bing Search API resource in Azure
- [ ] Add all API keys to `.env` file
- [ ] Test with `python api_connectors_real.py`
- [ ] Run demo with `streamlit run demo5_trend_research_real.py`
- [ ] Try a custom research question
- [ ] Verify graceful handling of missing APIs
- [ ] Export results as JSON

---

## Support & Resources

### Official Documentation

- **Twitter API:** https://developer.twitter.com/en/docs
- **Reddit API:** https://www.reddit.com/dev/api/
- **Google Trends:** https://github.com/GeneralMills/pytrends
- **Bing Search:** https://docs.microsoft.com/en-us/bing/search-apis/
- **TikTok API:** https://developers.tiktok.com/

### Community Resources

- **Twitter API Community:** https://twittercommunity.com/
- **Reddit API Help:** r/redditdev
- **Stack Overflow:** Tag questions with specific API names

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review API documentation
3. Check API status pages
4. Test with mock APIs first
5. Verify `.env` configuration

---

## Next Steps

Once you have real APIs configured:

1. **Test thoroughly** with different queries
2. **Monitor costs** and API usage
3. **Implement caching** to reduce API calls
4. **Add error logging** for production
5. **Create dashboards** to track API health
6. **Set up alerts** for quota limits
7. **Document** your specific use cases

---

**Ready to use real APIs!** 🚀

For questions or issues, refer to the official API documentation or create an issue in the repository.
