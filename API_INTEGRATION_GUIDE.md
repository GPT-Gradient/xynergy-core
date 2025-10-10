# ASO Platform - Free API Integration Guide

**Date**: October 9, 2025
**Status**: Configuration Ready
**Cost**: $0/month (all free APIs)

---

## 📋 OVERVIEW

This guide covers the setup of 5 free API integrations for the ASO platform:

1. **Google Search Console** - Keyword rankings, impressions, CTR
2. **Google Trends** - Trending topics, search volume estimates
3. **Google Analytics 4** - Traffic data, user behavior
4. **Reddit API** - Social signals, trending discussions
5. **Twitter API** - Social mentions, trending topics

**Total Setup Time**: ~2 hours
**Monthly Cost**: $0 (all free tier)

---

## 🔑 API 1: GOOGLE SEARCH CONSOLE (GSC)

### Purpose:
- Real keyword ranking data
- Impressions and clicks
- CTR by keyword
- Page performance metrics

### Setup Steps:

#### 1. Enable the API
```bash
gcloud services enable searchconsole.googleapis.com \
  --project=xynergy-dev-1757909467
```

#### 2. Create OAuth 2.0 Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Name: "ASO Platform GSC Integration"
5. Authorized redirect URIs:
   - `https://aso-engine-vgjxy554mq-uc.a.run.app/api/oauth/gsc/callback`
6. Download JSON credentials

#### 3. Store Credentials
```bash
# Upload to Secret Manager
gcloud secrets create gsc-oauth-credentials \
  --project=xynergy-dev-1757909467 \
  --data-file=client_secret.json

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding gsc-oauth-credentials \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 4. Add Property to GSC
1. Go to: https://search.google.com/search-console
2. Add your property (e.g., example.com)
3. Verify ownership via HTML file, DNS, or Google Analytics

### API Endpoints (ASO Engine):
- `POST /api/integrations/gsc/authorize` - Start OAuth flow
- `GET /api/integrations/gsc/callback` - OAuth callback
- `POST /api/integrations/gsc/sync` - Sync keyword data
- `GET /api/integrations/gsc/keywords` - Get keyword performance

### Data Collected:
- Keywords with impressions/clicks
- Average position
- CTR by keyword
- Query performance over time

### Rate Limits:
- 1,200 queries per minute
- 100,000 queries per day
- **Cost**: FREE

---

## 📈 API 2: GOOGLE TRENDS

### Purpose:
- Trending search topics
- Regional interest
- Related queries
- Search volume trends

### Setup Steps:

#### 1. Install Python Library
```bash
# Already in requirements: pytrends
pip install pytrends
```

#### 2. No API Key Required!
Google Trends is publicly accessible via the `pytrends` library. No authentication needed.

### API Endpoints (ASO Engine):
- `GET /api/trends/search?keyword=<term>` - Get trend data
- `GET /api/trends/related?keyword=<term>` - Related queries
- `GET /api/trends/trending` - Currently trending topics
- `GET /api/trends/regional?keyword=<term>` - Regional interest

### Data Collected:
- Search volume trends (relative)
- Rising and top related queries
- Regional breakdown
- Category trends

### Rate Limits:
- ~400 requests per day (soft limit)
- Must include delays (2-3 seconds between requests)
- **Cost**: FREE

---

## 📊 API 3: GOOGLE ANALYTICS 4 (GA4)

### Purpose:
- Traffic metrics
- User behavior
- Conversion data
- Page performance

### Setup Steps:

#### 1. Enable the API
```bash
gcloud services enable analyticsdata.googleapis.com \
  --project=xynergy-dev-1757909467
```

#### 2. Create Service Account
```bash
# Create SA for GA4 access
gcloud iam service-accounts create ga4-reader \
  --project=xynergy-dev-1757909467 \
  --display-name="GA4 Data Reader"

# Generate key
gcloud iam service-accounts keys create ga4-key.json \
  --iam-account=ga4-reader@xynergy-dev-1757909467.iam.gserviceaccount.com

# Store in Secret Manager
gcloud secrets create ga4-service-account \
  --data-file=ga4-key.json

# Grant access
gcloud secrets add-iam-policy-binding ga4-service-account \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 3. Grant GA4 Access
1. Go to: https://analytics.google.com/
2. Admin → Property Access Management
3. Add user: `ga4-reader@xynergy-dev-1757909467.iam.gserviceaccount.com`
4. Role: "Viewer"

### API Endpoints (ASO Engine):
- `POST /api/integrations/ga4/sync` - Sync traffic data
- `GET /api/integrations/ga4/traffic` - Get traffic metrics
- `GET /api/integrations/ga4/pages` - Page performance
- `GET /api/integrations/ga4/conversions` - Conversion data

### Data Collected:
- Sessions, users, page views
- Bounce rate, session duration
- Traffic sources
- Landing page performance
- Conversion metrics

### Rate Limits:
- 25,000 requests per day (Data API v1)
- 10 concurrent requests
- **Cost**: FREE (up to 25K requests/day)

---

## 🔴 API 4: REDDIT API

### Purpose:
- Trending discussions
- Social signals
- Topic popularity
- Community insights

### Setup Steps:

#### 1. Create Reddit App
1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in details:
   - Name: "ASO Platform Integration"
   - App type: "script"
   - Description: "ASO keyword and trend monitoring"
   - About URL: https://your-domain.com
   - Redirect URI: `https://aso-engine-vgjxy554mq-uc.a.run.app/api/oauth/reddit/callback`
4. Click "Create app"
5. Note the client ID and secret

#### 2. Store Credentials
```bash
# Store Reddit credentials
echo -n "your-client-id" | gcloud secrets create reddit-client-id --data-file=-
echo -n "your-client-secret" | gcloud secrets create reddit-client-secret --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding reddit-client-id \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding reddit-client-secret \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### API Endpoints (ASO Engine):
- `GET /api/integrations/reddit/trending` - Trending posts
- `GET /api/integrations/reddit/search?q=<keyword>` - Search discussions
- `GET /api/integrations/reddit/subreddit/<name>` - Subreddit data

### Data Collected:
- Trending posts by keyword
- Upvotes, comments
- Subreddit activity
- User engagement metrics

### Rate Limits:
- 60 requests per minute
- 600 requests per 10 minutes
- **Cost**: FREE

---

## 🐦 API 5: TWITTER API (X API)

### Purpose:
- Social mentions
- Trending hashtags
- Brand monitoring
- Viral content detection

### Setup Steps:

#### 1. Apply for Developer Account
1. Go to: https://developer.twitter.com/
2. Click "Sign up" → "Developer Portal"
3. Apply for Essential access (FREE tier)
4. Fill out use case: "SEO and content trend monitoring"
5. Wait for approval (~24 hours)

#### 2. Create App & Get Keys
1. In Developer Portal → "Projects & Apps"
2. Create new App
3. Note:
   - API Key (Consumer Key)
   - API Secret Key (Consumer Secret)
   - Bearer Token

#### 3. Store Credentials
```bash
# Store Twitter credentials
echo -n "your-api-key" | gcloud secrets create twitter-api-key --data-file=-
echo -n "your-api-secret" | gcloud secrets create twitter-api-secret --data-file=-
echo -n "your-bearer-token" | gcloud secrets create twitter-bearer-token --data-file=-

# Grant access
for secret in twitter-api-key twitter-api-secret twitter-bearer-token; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

### API Endpoints (ASO Engine):
- `GET /api/integrations/twitter/search?q=<keyword>` - Search tweets
- `GET /api/integrations/twitter/trending` - Trending topics
- `GET /api/integrations/twitter/mentions?brand=<name>` - Brand mentions

### Data Collected:
- Tweet volume by keyword
- Engagement (likes, retweets)
- Trending hashtags
- Influencer mentions

### Rate Limits (Essential - FREE tier):
- 500,000 tweets per month
- 50 requests per 15 minutes (search)
- **Cost**: FREE (Essential tier)

---

## 🔐 SECURITY BEST PRACTICES

### Secret Management:
```bash
# List all secrets
gcloud secrets list --project=xynergy-dev-1757909467

# View secret versions
gcloud secrets versions list <SECRET_NAME>

# Rotate secrets
gcloud secrets versions add <SECRET_NAME> --data-file=new-secret.json
```

### Environment Variables (ASO Engine):
```bash
# Update Cloud Run service with secret references
gcloud run services update aso-engine \
  --project=xynergy-dev-1757909467 \
  --region=us-central1 \
  --update-secrets=GSC_OAUTH_CREDENTIALS=gsc-oauth-credentials:latest,\
GA4_SERVICE_ACCOUNT=ga4-service-account:latest,\
REDDIT_CLIENT_ID=reddit-client-id:latest,\
REDDIT_CLIENT_SECRET=reddit-client-secret:latest,\
TWITTER_BEARER_TOKEN=twitter-bearer-token:latest
```

---

## 📊 DATA COLLECTION SCHEDULE

### Recommended Frequencies:

| API | Frequency | Scheduler Job | Daily Quota Used |
|-----|-----------|---------------|------------------|
| Google Search Console | Daily (6am) | `gsc-sync-daily` | ~50 queries |
| Google Trends | 3x daily | `trends-sync-8hourly` | ~30 requests |
| Google Analytics 4 | Daily (7am) | `ga4-sync-daily` | ~20 requests |
| Reddit | Hourly | `reddit-trending-hourly` | ~400 requests |
| Twitter | 2x daily | `twitter-trends-12hourly` | ~100 tweets |

**Total Daily Requests**: <1,000 across all APIs
**Total Monthly Cost**: $0 (all free tiers)

---

## 🧪 TESTING INTEGRATIONS

### Test Script:
```bash
#!/bin/bash
# Test all API integrations

ASO_ENGINE_URL="https://aso-engine-vgjxy554mq-uc.a.run.app"
TOKEN=$(gcloud auth print-identity-token)

echo "Testing API Integrations..."

# Test Google Trends (no auth required)
echo "1. Testing Google Trends..."
curl -H "Authorization: Bearer $TOKEN" \
  "$ASO_ENGINE_URL/api/trends/search?keyword=ai+seo"

# Test GSC (requires OAuth setup)
echo "2. Testing Google Search Console..."
curl -H "Authorization: Bearer $TOKEN" \
  "$ASO_ENGINE_URL/api/integrations/gsc/authorize"

# Test GA4 (requires service account)
echo "3. Testing Google Analytics 4..."
curl -H "Authorization: Bearer $TOKEN" \
  "$ASO_ENGINE_URL/api/integrations/ga4/traffic"

# Test Reddit
echo "4. Testing Reddit API..."
curl -H "Authorization: Bearer $TOKEN" \
  "$ASO_ENGINE_URL/api/integrations/reddit/trending"

# Test Twitter
echo "5. Testing Twitter API..."
curl -H "Authorization: Bearer $TOKEN" \
  "$ASO_ENGINE_URL/api/integrations/twitter/trending"
```

---

## 📈 EXPECTED DATA VOLUME

### Per Day:
- GSC: ~500 keywords with performance data
- Trends: ~50 trending topics
- GA4: ~100 pages with traffic metrics
- Reddit: ~200 trending posts
- Twitter: ~500 trending tweets

### Storage Requirements:
- Daily: ~5 MB
- Monthly: ~150 MB
- Yearly: ~1.8 GB

**BigQuery Cost**: ~$0.04/month (storage)

---

## 🎯 IMPLEMENTATION CHECKLIST

### Phase 1: Credentials Setup (30 minutes)
- [ ] Enable required Google APIs
- [ ] Create OAuth credentials for GSC
- [ ] Create GA4 service account
- [ ] Register Reddit app
- [ ] Apply for Twitter developer access
- [ ] Store all secrets in Secret Manager

### Phase 2: ASO Engine Updates (1 hour)
- [ ] Add integration endpoints
- [ ] Implement OAuth flows
- [ ] Add data sync functions
- [ ] Update requirements.txt
- [ ] Deploy updated service

### Phase 3: Testing (30 minutes)
- [ ] Test each API individually
- [ ] Verify data collection
- [ ] Check BigQuery storage
- [ ] Validate rate limits

### Phase 4: Automation (30 minutes)
- [ ] Create scheduler jobs for each API
- [ ] Set up monitoring alerts
- [ ] Configure error handling

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: GSC OAuth Fails
**Cause**: Redirect URI mismatch
**Solution**: Ensure redirect URI in OAuth config matches exactly:
```
https://aso-engine-vgjxy554mq-uc.a.run.app/api/oauth/gsc/callback
```

### Issue 2: GA4 403 Errors
**Cause**: Service account not granted access
**Solution**: Add service account email to GA4 property with Viewer role

### Issue 3: Reddit Rate Limit
**Cause**: Too many requests
**Solution**: Implement exponential backoff:
```python
import time
time.sleep(2)  # 2 seconds between requests
```

### Issue 4: Twitter Rate Limit
**Cause**: Exceeded 50 requests/15min
**Solution**: Cache trending data, only refresh every 15 minutes

---

## 📞 NEXT STEPS

After completing this setup:

1. **Test all integrations** using the test script above
2. **Create scheduler jobs** for automated data collection
3. **Monitor quota usage** in GCP Console
4. **Set up alerts** for API errors
5. **Document API keys** in secure location

---

**Estimated Total Setup Time**: 2 hours
**Monthly Cost**: $0 (all free)
**Data Value**: $500+/month (equivalent to paid SEO tools)

---

*Created for ASO Platform*
*Project: xynergy-dev-1757909467*
*Date: October 9, 2025*
