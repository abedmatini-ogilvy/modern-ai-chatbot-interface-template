# API Setup Guides

> **Purpose**: Step-by-step instructions to obtain API credentials for each service  
> **Last Updated**: November 2024

---

## Table of Contents
1. [Twitter/X API](#1-twitterx-api)
2. [Reddit API](#2-reddit-api)
3. [Google Trends (pytrends)](#3-google-trends-pytrends)
4. [SerpAPI (Web Search)](#4-serpapi-web-search)
5. [Brave Search API](#5-brave-search-api)
6. [TikTok API](#6-tiktok-api)
7. [Google Gemini](#7-google-gemini)
8. [Azure OpenAI](#8-azure-openai)
9. [Nitter (Experimental)](#9-nitter-experimental)

---

## 1. Twitter/X API

### Free Tier Limits
- **Read**: 1,500 tweets/month
- **Rate**: 1 request/second
- **Access**: API v2 only

### Setup Steps

1. **Go to Twitter Developer Portal**
   ```
   https://developer.twitter.com/en/portal/dashboard
   ```

2. **Sign up / Sign in**
   - Use your Twitter/X account
   - Complete developer agreement

3. **Create a Project**
   - Click "Create Project"
   - Name: `TrendResearchBot`
   - Use case: "Research"
   - Description: "Marketing trend research application"

4. **Create an App within the Project**
   - App name: `trend-research-app`
   - Save your keys immediately!

5. **Get Your Credentials**
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Bearer Token (for app-only auth)
   - Access Token & Secret (for user auth)

6. **Add to `.env`**
   ```bash
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ```

7. **Test Connection**
   ```bash
   cd backend
   python -c "
   import tweepy
   import os
   client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
   tweets = client.search_recent_tweets(query='python', max_results=10)
   print(f'Found {len(tweets.data)} tweets')
   "
   ```

### Troubleshooting
- **403 Forbidden**: Check if app has read permissions
- **429 Rate Limit**: Wait 15 minutes or check monthly quota
- **401 Unauthorized**: Regenerate bearer token

---

## 2. Reddit API

### Free Tier Limits
- **Rate**: 60 requests/minute (100 with OAuth)
- **Access**: Full read access to public subreddits
- **No monthly limits** for reasonable use

### Setup Steps

1. **Go to Reddit App Preferences**
   ```
   https://www.reddit.com/prefs/apps
   ```

2. **Create Application**
   - Scroll to bottom, click "create another app..."
   - Select **"script"** type (for personal/backend use)
   - Name: `TrendResearchBot`
   - Redirect URI: `http://localhost:8000` (not used but required)

3. **Get Your Credentials**
   - **Client ID**: The string under your app name (looks like: `aBcDeFgHiJk`)
   - **Client Secret**: The "secret" field

4. **Add to `.env`**
   ```bash
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=TrendResearchBot/1.0 by /u/your_username
   ```

5. **Test Connection**
   ```bash
   cd backend
   python -c "
   import praw
   import os
   reddit = praw.Reddit(
       client_id=os.getenv('REDDIT_CLIENT_ID'),
       client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
       user_agent=os.getenv('REDDIT_USER_AGENT')
   )
   for post in reddit.subreddit('python').hot(limit=5):
       print(f'{post.score}: {post.title[:50]}')
   "
   ```

### Troubleshooting
- **401 Error**: Check client ID/secret
- **User Agent Required**: Must include a unique user agent string
- **Read-only mode**: Normal for script apps, full read access works

---

## 3. Google Trends (pytrends)

### Free Tier Limits
- **No API key required** (unofficial library)
- **Rate**: ~10 requests/minute recommended
- **Risk**: Google may block if overused

### Setup Steps

1. **Install pytrends**
   ```bash
   pip install pytrends
   ```

2. **No credentials needed!**
   pytrends uses web scraping, no API key required

3. **Test Connection**
   ```bash
   cd backend
   python -c "
   from pytrends.request import TrendReq
   pytrends = TrendReq(hl='en-US', tz=360)
   pytrends.build_payload(['python programming'], timeframe='today 3-m')
   data = pytrends.interest_over_time()
   print(data.head())
   "
   ```

### Best Practices
- Add delays between requests (1-2 seconds)
- Use proxies if getting blocked
- Cache results to reduce requests
- Limit to 5 keywords per request

### Troubleshooting
- **429 Too Many Requests**: Add delays, reduce frequency
- **Empty results**: Try different keywords or timeframes
- **Connection errors**: Google may be blocking, use VPN/proxy

---

## 4. SerpAPI (Web Search)

### Free Tier Limits
- **100 searches/month**
- **Access**: Google, Bing, Yahoo, and more
- **Features**: Organic results, snippets, related searches

### Setup Steps

1. **Go to SerpAPI**
   ```
   https://serpapi.com/
   ```

2. **Create Free Account**
   - Click "Get Started" or "Sign Up"
   - Verify email

3. **Get API Key**
   - Dashboard → API Key
   - Copy your key

4. **Add to `.env`**
   ```bash
   SERPAPI_API_KEY=your_api_key
   ```

5. **Test Connection**
   ```bash
   cd backend
   python -c "
   from serpapi import GoogleSearch
   import os
   params = {
       'q': 'Gen Z marketing trends',
       'api_key': os.getenv('SERPAPI_API_KEY')
   }
   search = GoogleSearch(params)
   results = search.get_dict()
   for r in results.get('organic_results', [])[:3]:
       print(f\"{r['title']}: {r['link']}\")
   "
   ```

### Troubleshooting
- **Invalid API key**: Check for typos, regenerate if needed
- **Quota exceeded**: Check dashboard for usage
- **No results**: Try simpler query terms

---

## 5. Brave Search API

### Free Tier Limits
- **2,000 queries/month** (generous!)
- **Access**: Web search, news, videos
- **Privacy-focused**: Good alternative to Google

### Setup Steps

1. **Go to Brave Search API**
   ```
   https://brave.com/search/api/
   ```

2. **Create Account**
   - Click "Get Started"
   - Choose "Free" plan
   - Create account

3. **Get API Key**
   - Dashboard → API Keys
   - Create new key
   - Copy the key

4. **Add to `.env`**
   ```bash
   BRAVE_SEARCH_API_KEY=your_api_key
   ```

5. **Test Connection**
   ```bash
   cd backend
   python -c "
   import requests
   import os
   headers = {
       'Accept': 'application/json',
       'X-Subscription-Token': os.getenv('BRAVE_SEARCH_API_KEY')
   }
   params = {'q': 'Gen Z marketing trends', 'count': 5}
   response = requests.get(
       'https://api.search.brave.com/res/v1/web/search',
       headers=headers,
       params=params
   )
   data = response.json()
   for r in data.get('web', {}).get('results', [])[:3]:
       print(f\"{r['title']}: {r['url']}\")
   "
   ```

### Troubleshooting
- **401 Unauthorized**: Check API key
- **429 Rate Limit**: 1 request/second limit
- **Empty results**: Try broader search terms

---

## 6. TikTok API

### Options Available

#### Option A: TikTok Creative Center (Recommended for MVP)
- **Access**: Trending data, hashtags
- **Free**: Yes, but limited data
- **URL**: https://ads.tiktok.com/business/creativecenter/

#### Option B: TikTok Research API
- **Access**: Full search, user data
- **Free**: No, requires business account
- **URL**: https://developers.tiktok.com/

### Setup Steps (Creative Center)

1. **Go to TikTok Creative Center**
   ```
   https://ads.tiktok.com/business/creativecenter/
   ```

2. **Create TikTok Business Account**
   - Sign up with email
   - May need to create a TikTok Ads account (free)

3. **Access Trend Data**
   - Navigate to "Trends" section
   - Note: May need to scrape or use unofficial methods

4. **Alternative: TikTok Display API**
   ```
   https://developers.tiktok.com/
   ```
   - Create developer account
   - Apply for API access
   - Wait for approval (can take days/weeks)

### Notes
- TikTok API access is more restricted than other platforms
- For MVP, consider using mock data for TikTok
- Creative Center provides trending hashtags without API

---

## 7. Google Gemini

### Free Tier Limits
- **60 requests/minute**
- **1 million tokens/day**
- **Models**: Gemini Pro, Gemini Pro Vision

### Setup Steps

1. **Go to Google AI Studio**
   ```
   https://makersuite.google.com/
   ```

2. **Sign in with Google Account**

3. **Get API Key**
   - Click "Get API Key"
   - Create new key or use existing project
   - Copy the key

4. **Add to `.env`**
   ```bash
   GOOGLE_AI_API_KEY=your_api_key
   ```

5. **Test Connection**
   ```bash
   cd backend
   python -c "
   import google.generativeai as genai
   import os
   genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
   model = genai.GenerativeModel('gemini-pro')
   response = model.generate_content('Say hello in 3 words')
   print(response.text)
   "
   ```

### Troubleshooting
- **Invalid API key**: Regenerate in AI Studio
- **Quota exceeded**: Check usage in Google Cloud Console
- **Content blocked**: Gemini has safety filters

---

## 8. Azure OpenAI

### Pricing (Pay-as-you-go)
- **GPT-4**: ~$0.03/1K tokens (input), ~$0.06/1K tokens (output)
- **GPT-3.5**: ~$0.001/1K tokens
- **No free tier** (but minimal cost for testing)

### Setup Steps

1. **Go to Azure Portal**
   ```
   https://portal.azure.com/
   ```

2. **Create Azure OpenAI Resource**
   - Search "Azure OpenAI"
   - Click "Create"
   - Select subscription and resource group
   - Choose region (East US has most models)
   - Wait for deployment (~5-10 minutes)

3. **Deploy a Model**
   - Go to Azure OpenAI Studio
   - Click "Deployments" → "Create"
   - Select model (gpt-4, gpt-35-turbo)
   - Name your deployment (e.g., `gpt-4-deployment`)

4. **Get Credentials**
   - Keys and Endpoint: Azure Portal → Your resource → Keys and Endpoint
   - Copy Key 1 and Endpoint

5. **Add to `.env`**
   ```bash
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
   ```

6. **Test Connection**
   ```bash
   cd backend
   python -c "
   from openai import AzureOpenAI
   import os
   client = AzureOpenAI(
       api_key=os.getenv('AZURE_OPENAI_API_KEY'),
       api_version='2024-02-15-preview',
       azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
   )
   response = client.chat.completions.create(
       model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
       messages=[{'role': 'user', 'content': 'Say hello in 3 words'}]
   )
   print(response.choices[0].message.content)
   "
   ```

### Troubleshooting
- **404 Not Found**: Check deployment name matches
- **401 Unauthorized**: Check API key
- **Region unavailable**: Some models only in certain regions

---

## 9. Nitter (Experimental)

### What is Nitter?
- Open-source Twitter frontend
- No API key required
- Unofficial, may break
- Use as fallback only

### Public Instances
```
https://nitter.net
https://nitter.it
https://nitter.nl
https://nitter.1d4.us
```

### Usage Notes
- Instances can go down frequently
- Implement multiple instance fallback
- Respect rate limits (be polite)
- No official support

### Test Connection
```bash
cd backend
python -c "
import requests
# Try multiple instances
instances = ['nitter.net', 'nitter.it', 'nitter.nl']
for instance in instances:
    try:
        response = requests.get(f'https://{instance}/search?q=python', timeout=5)
        print(f'{instance}: {response.status_code}')
    except Exception as e:
        print(f'{instance}: Failed - {e}')
"
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files**
   ```bash
   # .gitignore should include:
   .env
   .env.local
   .env.*.local
   ```

2. **Use `.env.template` for documentation**
   - Include all variable names
   - Use placeholder values
   - Commit this file

3. **Rotate keys regularly**
   - Set calendar reminders
   - Use different keys for dev/prod

4. **Limit API key permissions**
   - Read-only when possible
   - Restrict to specific IPs if available

5. **Monitor usage**
   - Check dashboards weekly
   - Set up billing alerts

---

## ✅ Credential Checklist

Use this to track your progress:

| Service | Account Created | API Key Obtained | Tested | Added to .env |
|---------|----------------|------------------|--------|---------------|
| Twitter/X | ⬜ | ⬜ | ⬜ | ⬜ |
| Reddit | ⬜ | ⬜ | ⬜ | ⬜ |
| Google Trends | ✅ N/A | ✅ N/A | ⬜ | ✅ N/A |
| SerpAPI | ⬜ | ⬜ | ⬜ | ⬜ |
| Brave Search | ⬜ | ⬜ | ⬜ | ⬜ |
| TikTok | ⬜ | ⬜ | ⬜ | ⬜ |
| Google Gemini | ⬜ | ⬜ | ⬜ | ⬜ |
| Azure OpenAI | ⬜ | ⬜ | ⬜ | ⬜ |

---

## 📞 Support Links

| Service | Documentation | Support |
|---------|--------------|---------|
| Twitter | [Developer Docs](https://developer.twitter.com/en/docs) | [Community](https://twittercommunity.com/) |
| Reddit | [API Docs](https://www.reddit.com/dev/api/) | [r/redditdev](https://reddit.com/r/redditdev) |
| pytrends | [GitHub](https://github.com/GeneralMills/pytrends) | [Issues](https://github.com/GeneralMills/pytrends/issues) |
| SerpAPI | [Docs](https://serpapi.com/search-api) | [Email](mailto:support@serpapi.com) |
| Brave | [API Docs](https://brave.com/search/api/) | [Support](https://brave.com/contact/) |
| Gemini | [AI Studio](https://ai.google.dev/docs) | [Discord](https://discord.gg/google-dev-community) |
| Azure OpenAI | [Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/) | [Azure Support](https://azure.microsoft.com/support/) |
