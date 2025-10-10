# Xynergy Platform - Monitoring & Alerting Setup

**Phase 3: Reliability & Monitoring**

This directory contains GCP monitoring dashboard and alert policy configurations.

---

## 📊 Dashboard Setup

The dashboard provides real-time visibility into:
- Request rate and latency
- Memory and CPU utilization
- Error rates
- Instance scaling
- Estimated costs

### Deploy Dashboard

```bash
# From project root
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard_config.json

# View in console
# https://console.cloud.google.com/monitoring/dashboards?project=xynergy-dev-1757909467
```

---

## 🚨 Alert Policies

Alert policies are configured to detect:
1. High error rates (>5% of requests)
2. High memory usage (>80%)
3. Service unavailability
4. Abnormal latency

### Setup Notification Channels

**Email notifications:**
```bash
gcloud alpha monitoring channels create \
  --display-name="Xynergy Operations" \
  --type=email \
  --channel-labels=email_address=ops@xynergy.com
```

**Slack notifications:**
```bash
# First, create a Slack webhook at https://api.slack.com/messaging/webhooks
# Then create the channel:
gcloud alpha monitoring channels create \
  --display-name="Xynergy Slack Alerts" \
  --type=slack \
  --channel-labels=url=YOUR_WEBHOOK_URL
```

### Deploy Alert Policies

```bash
# List notification channels
gcloud alpha monitoring channels list

# Copy channel ID, then deploy alerts
# Edit alert_policies.sh to add your channel ID
chmod +x monitoring/alert_policies.sh
./monitoring/alert_policies.sh
```

---

## 📈 Custom Metrics

The platform can export custom business metrics:

- AI generation count
- Cache hit rates
- Workflow completion times
- Content quality scores

See `shared/custom_metrics.py` for implementation.

---

## 🔍 Distributed Tracing

View request traces in Cloud Trace:
https://console.cloud.google.com/traces?project=xynergy-dev-1757909467

Traces show:
- End-to-end request flow
- Service dependencies
- Performance bottlenecks
- Error propagation

---

## 📚 Additional Resources

- **GCP Monitoring Docs**: https://cloud.google.com/monitoring/docs
- **Cloud Trace Docs**: https://cloud.google.com/trace/docs
- **Alert Policy Best Practices**: https://cloud.google.com/monitoring/alerts/concepts-best-practices
