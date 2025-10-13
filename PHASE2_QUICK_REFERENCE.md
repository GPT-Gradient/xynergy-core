# Phase 2 Quick Reference

**Status:** ✅ COMPLETE
**Time:** 2.5 hours backend work + 1.5 hours manual OAuth setup
**Ready For:** OAuth credential configuration

---

## 🚀 Quick Start

### Enable OAuth (Complete Flow)
```bash
# 1. Run interactive OAuth setup (enter credentials when prompted)
./scripts/phase2-oauth-setup.sh

# 2. Deploy services with OAuth
./scripts/deploy-oauth-services.sh

# 3. Verify deployment
./scripts/verify-deployment.sh

# 4. Run integration tests
./tests/integration-tests.sh
```

### Deploy Individual Service
```bash
./scripts/deploy-oauth-services.sh slack     # Slack only
./scripts/deploy-oauth-services.sh gmail     # Gmail only
./scripts/deploy-oauth-services.sh calendar  # Calendar only
```

### Set Up Monitoring
```bash
./scripts/setup-monitoring.sh  # Creates dashboard + alerts
```

---

## 📊 OAuth Status Check

```bash
# Check if services are in mock mode or OAuth mode
curl https://slack-intelligence-service-835612502919.us-central1.run.app/
curl https://gmail-intelligence-service-835612502919.us-central1.run.app/
curl https://calendar-intelligence-service-835612502919.us-central1.run.app/

# Look for "mockMode": true/false in response
```

---

## 🔑 Required Credentials

### Slack (4 secrets)
- `SLACK_BOT_TOKEN` - Bot User OAuth Token (xoxb-...)
- `SLACK_CLIENT_ID` - App Client ID
- `SLACK_CLIENT_SECRET` - App Client Secret
- `SLACK_SIGNING_SECRET` - App Signing Secret

**Get from:** https://api.slack.com/apps

### Gmail + Calendar (2 secrets, shared)
- `GMAIL_CLIENT_ID` - OAuth 2.0 Client ID (.apps.googleusercontent.com)
- `GMAIL_CLIENT_SECRET` - OAuth 2.0 Client Secret

**Get from:** https://console.cloud.google.com → APIs & Services → Credentials

---

## 🧪 Testing Commands

### Basic Tests (No Auth Required)
```bash
./tests/integration-tests.sh
```

Tests:
- Gateway health
- Unauthenticated access (expects 401)
- OAuth status
- Service availability
- Performance

### Full Tests (Auth Required)
```bash
export AUTH_TOKEN="your-firebase-token"
./tests/integration-tests.sh
```

Additional tests:
- Authenticated API calls
- Data structure validation
- API functionality
- End-to-end flows

---

## 📁 New Files Created

### Scripts
- `scripts/phase2-oauth-setup.sh` - Interactive OAuth setup
- `scripts/deploy-oauth-services.sh` - Deploy with OAuth
- `scripts/setup-monitoring.sh` - Monitoring configuration
- `tests/integration-tests.sh` - Automated test suite

### Configuration
- `monitoring/dashboard-config.json` - Cloud Monitoring dashboard
- Service configs updated with OAuth support:
  - `slack-intelligence-service/src/config/config.ts`
  - `gmail-intelligence-service/src/config.ts`
  - `calendar-intelligence-service/src/config/config.ts`

### Services Updated
- `slack-intelligence-service/src/services/slackService.ts` ✅ OAuth ready
- `gmail-intelligence-service/src/services/gmailService.ts` ✅ OAuth ready
- `calendar-intelligence-service/src/services/calendarService.ts` ✅ Created new

### Documentation
- `PHASE2_COMPLETE.md` - Complete Phase 2 documentation
- `PHASE2_QUICK_REFERENCE.md` - This file
- `OAuth_SETUP_GUIDE.md` - Already existed, still valid

---

## 🎯 Service Behavior

### Mock Mode (Default)
```json
{
  "data": {...},
  "mockMode": true  ← Indicates mock data
}
```

### OAuth Mode (After Credentials)
```json
{
  "data": {...}  ← No mockMode flag = real data
}
```

---

## 🔧 Troubleshooting

### Services Still in Mock Mode After Deploy
1. Check secrets exist:
   ```bash
   gcloud secrets list --project=xynergy-dev-1757909467 | grep SLACK
   gcloud secrets list --project=xynergy-dev-1757909467 | grep GMAIL
   ```

2. Check service has access to secrets:
   ```bash
   gcloud run services describe slack-intelligence-service --region us-central1 | grep secrets
   ```

3. Check service logs:
   ```bash
   gcloud run services logs read slack-intelligence-service --region us-central1
   ```

### OAuth Credentials Not Working
1. Verify redirect URIs match exactly
2. Check scopes are configured correctly
3. Ensure OAuth consent screen is published
4. Verify credentials are for correct project

### Tests Failing
1. Check services are deployed:
   ```bash
   gcloud run services list --region us-central1
   ```

2. Verify gateway is healthy:
   ```bash
   curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health
   ```

3. Run deployment verification:
   ```bash
   ./scripts/verify-deployment.sh
   ```

---

## 📊 Monitoring URLs

**Dashboard:**
```
https://console.cloud.google.com/monitoring/dashboards?project=xynergy-dev-1757909467
```

**Alerts:**
```
https://console.cloud.google.com/monitoring/alerting?project=xynergy-dev-1757909467
```

**Logs:**
```
https://console.cloud.google.com/logs?project=xynergy-dev-1757909467
```

---

## ✅ Verification Checklist

Phase 2 is complete when:
- [ ] OAuth setup script runs successfully
- [ ] Credentials stored in Secret Manager
- [ ] Services deployed with `--set-secrets`
- [ ] Services respond (not 503)
- [ ] OAuth status check shows mode correctly
- [ ] Integration tests pass
- [ ] Monitoring dashboard visible
- [ ] Alert policies created

---

## 💡 Pro Tips

1. **Test in mock mode first** - Ensure all endpoints work before adding OAuth
2. **Use interactive script** - `phase2-oauth-setup.sh` handles IAM bindings automatically
3. **Deploy incrementally** - Test one service at a time (slack, then gmail, then calendar)
4. **Check logs immediately** - After deploy, check for OAuth initialization messages
5. **Set up alerts** - Configure notification channels to catch issues early

---

## 🎓 Learning Resources

**Slack OAuth:**
- https://api.slack.com/authentication/oauth-v2
- https://api.slack.com/docs/token-types

**Google OAuth:**
- https://developers.google.com/identity/protocols/oauth2/web-server
- https://developers.google.com/gmail/api/quickstart/nodejs
- https://developers.google.com/calendar/api/quickstart/nodejs

**Cloud Run Secrets:**
- https://cloud.google.com/run/docs/configuring/secrets

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Can't create Slack app | Need Slack workspace admin access |
| Can't create Google OAuth | Need Google Cloud project owner/editor role |
| Secrets not accessible | Run IAM binding commands in oauth-setup script |
| Services won't deploy | Check Docker build logs: `gcloud builds log` |
| Tests fail with 401 | Set AUTH_TOKEN environment variable |
| Mock mode won't disable | Check secrets mounted: `gcloud run services describe` |

---

**Status:** READY FOR OAUTH CREDENTIALS
**Next Step:** Run `./scripts/phase2-oauth-setup.sh`
