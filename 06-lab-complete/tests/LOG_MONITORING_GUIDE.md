# 📊 Log Monitoring Guide

> **Hướng dẫn đọc và phân tích logs cho Production AI Agent**

---

## 🎯 Mục Lục

1. [Cấu Trúc Log](#cấu-trúc-log)
2. [Đọc Logs Local](#đọc-logs-local)
3. [Đọc Logs Railway](#đọc-logs-railway)
4. [Đọc Logs Render](#đọc-logs-render)
5. [Nhận Diện Lỗi](#nhận-diện-lỗi)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## Cấu Trúc Log

### JSON Structured Logging

Agent sử dụng **structured JSON logging** để dễ parse và analyze:

```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "INFO",
  "msg": "request",
  "method": "POST",
  "path": "/ask",
  "status": 200,
  "ms": 123.4
}
```

### Log Levels

| Level | Ý Nghĩa | Khi Nào Xuất Hiện |
|-------|---------|-------------------|
| **DEBUG** | Chi tiết debug | Chỉ trong development |
| **INFO** | Thông tin bình thường | Mọi request, startup, shutdown |
| **WARNING** | Cảnh báo | Rate limit, slow response |
| **ERROR** | Lỗi | Exception, validation error |
| **CRITICAL** | Lỗi nghiêm trọng | System failure |

---

## Đọc Logs Local

### Docker Compose

```bash
# View all logs
docker compose logs

# Follow logs (real-time)
docker compose logs -f

# View agent logs only
docker compose logs -f agent

# View Redis logs
docker compose logs -f redis

# Last 100 lines
docker compose logs --tail 100 agent

# Filter by time
docker compose logs --since 10m agent
```

### Parse JSON Logs

```bash
# Install jq (JSON processor)
# macOS: brew install jq
# Linux: sudo apt install jq

# View logs as pretty JSON
docker compose logs agent | grep '{' | jq '.'

# Filter errors only
docker compose logs agent | grep '{' | jq 'select(.lvl=="ERROR")'

# Filter slow requests (> 1000ms)
docker compose logs agent | grep '{' | jq 'select(.ms > 1000)'

# Count requests by status
docker compose logs agent | grep '{' | jq '.status' | sort | uniq -c
```

### Example: Find All Errors

```bash
# Find all ERROR level logs
docker compose logs agent | grep '"lvl":"ERROR"'

# Output:
# {"ts":"2026-04-17 10:30:00","lvl":"ERROR","msg":"Database connection failed"}
# {"ts":"2026-04-17 10:31:00","lvl":"ERROR","msg":"Redis timeout"}
```

---

## Đọc Logs Railway

### Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs (real-time)
railway logs

# View logs with filter
railway logs --filter "ERROR"

# View logs from specific service
railway logs --service agent
```

### Railway Dashboard

1. Vào [railway.app](https://railway.app)
2. Select project
3. Click vào service (agent)
4. Tab **"Deployments"** → Click deployment
5. Tab **"Logs"**

**Features:**
- ✅ Real-time streaming
- ✅ Search/filter
- ✅ Download logs
- ✅ Time range selection

### Example: Find 500 Errors

**Search trong Railway Dashboard:**
```
"status":500
```

**Hoặc CLI:**
```bash
railway logs | grep '"status":500'
```

---

## Đọc Logs Render

### Render Dashboard

1. Vào [render.com](https://render.com)
2. Select service
3. Tab **"Logs"**

**Features:**
- ✅ Real-time streaming
- ✅ Search
- ✅ Filter by severity
- ✅ Download logs

### Render CLI (Beta)

```bash
# Install
npm install -g @render/cli

# Login
render login

# View logs
render logs <service-name>
```

### Example: Find Rate Limit Events

**Search trong Render Dashboard:**
```
429
```

**Hoặc:**
```
"status":429
```

---

## Nhận Diện Lỗi

### 1. 500 Internal Server Error

**Ý nghĩa:** Lỗi server, bug trong code

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "ERROR",
  "msg": "request",
  "method": "POST",
  "path": "/ask",
  "status": 500,
  "error": "division by zero"
}
```

**Cách tìm:**
```bash
# Local
docker compose logs agent | grep '"status":500'

# Railway
railway logs | grep '"status":500'

# Render
# Search: "status":500
```

**Cách fix:**
1. Đọc error message
2. Check stack trace
3. Fix bug trong code
4. Deploy lại

**Example:**
```bash
# Find 500 errors with context
docker compose logs agent | grep -A 5 -B 5 '"status":500'

# Output:
# {"ts":"2026-04-17 10:29:55","lvl":"INFO","msg":"request started"}
# {"ts":"2026-04-17 10:30:00","lvl":"ERROR","msg":"Redis connection failed"}
# {"ts":"2026-04-17 10:30:00","lvl":"ERROR","msg":"request","status":500}
# {"ts":"2026-04-17 10:30:05","lvl":"INFO","msg":"request finished"}
```

---

### 2. 429 Too Many Requests

**Ý nghĩa:** Rate limit triggered (> 5 requests/phút)

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "WARNING",
  "msg": "rate_limit_exceeded",
  "api_key": "abc123...",
  "requests": 6,
  "limit": 5
}
```

**Cách tìm:**
```bash
# Local
docker compose logs agent | grep '"status":429'

# Railway
railway logs | grep '429'

# Render
# Search: 429
```

**Cách xử lý:**
1. **Normal:** User đang spam → OK, rate limit working
2. **Problem:** Legitimate user bị block → Tăng limit

**Tăng rate limit:**
```bash
# Edit .env.local
RATE_LIMIT_PER_MINUTE=10

# Restart
docker compose restart agent

# Railway
railway variables set RATE_LIMIT_PER_MINUTE=10

# Render
# Dashboard → Environment → Update RATE_LIMIT_PER_MINUTE
```

---

### 3. 401 Unauthorized

**Ý nghĩa:** API key sai hoặc thiếu

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "WARNING",
  "msg": "unauthorized_access",
  "ip": "1.2.3.4",
  "path": "/ask"
}
```

**Cách tìm:**
```bash
docker compose logs agent | grep '"status":401'
```

**Cách fix:**
1. Check API key trong request
2. Verify API key trong environment variables

---

### 4. 422 Validation Error

**Ý nghĩa:** Input không hợp lệ (empty question, missing field)

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "WARNING",
  "msg": "validation_error",
  "field": "question",
  "error": "field required"
}
```

**Cách tìm:**
```bash
docker compose logs agent | grep '"status":422'
```

**Cách fix:**
1. Check request body
2. Ensure all required fields present

---

### 5. Redis Connection Error

**Ý nghĩa:** Không connect được Redis

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "ERROR",
  "msg": "redis_connection_failed",
  "error": "Connection refused"
}
```

**Cách tìm:**
```bash
docker compose logs agent | grep -i "redis"
```

**Cách fix:**
```bash
# Check Redis container
docker compose ps redis

# Restart Redis
docker compose restart redis

# Check Redis logs
docker compose logs redis

# Test connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

---

### 6. Slow Requests

**Ý nghĩa:** Request mất > 2 giây

**Log pattern:**
```json
{
  "ts": "2026-04-17 10:30:00",
  "lvl": "WARNING",
  "msg": "slow_request",
  "path": "/ask",
  "ms": 3456.7
}
```

**Cách tìm:**
```bash
# Find requests > 2000ms
docker compose logs agent | grep '{' | jq 'select(.ms > 2000)'
```

**Cách fix:**
1. Check database queries
2. Check external API calls
3. Add caching
4. Optimize code

---

## Monitoring & Alerts

### 1. Real-time Monitoring

**Local (Terminal):**
```bash
# Watch logs in real-time
watch -n 1 'docker compose logs --tail 20 agent'

# Count errors per minute
watch -n 60 'docker compose logs --since 1m agent | grep ERROR | wc -l'
```

**Railway:**
```bash
# Real-time logs
railway logs -f
```

**Render:**
- Dashboard → Logs → Auto-refresh enabled

---

### 2. Log Analysis Scripts

**Count requests by status:**
```bash
#!/bin/bash
# count_status.sh

docker compose logs agent | \
  grep '"status"' | \
  grep -o '"status":[0-9]*' | \
  cut -d: -f2 | \
  sort | uniq -c | \
  sort -rn

# Output:
#  150 200
#   10 429
#    5 401
#    2 500
```

**Find top slow requests:**
```bash
#!/bin/bash
# slow_requests.sh

docker compose logs agent | \
  grep '{' | \
  jq 'select(.ms != null) | {path: .path, ms: .ms}' | \
  jq -s 'sort_by(.ms) | reverse | .[0:10]'

# Output: Top 10 slowest requests
```

**Error rate:**
```bash
#!/bin/bash
# error_rate.sh

TOTAL=$(docker compose logs agent | grep '"status"' | wc -l)
ERRORS=$(docker compose logs agent | grep '"status":5' | wc -l)
RATE=$(echo "scale=2; $ERRORS / $TOTAL * 100" | bc)

echo "Total requests: $TOTAL"
echo "Errors: $ERRORS"
echo "Error rate: $RATE%"
```

---

### 3. Alerts (Advanced)

**Railway:**
- Dashboard → Settings → Notifications
- Configure Slack/Discord webhook

**Render:**
- Dashboard → Notifications
- Email alerts for deployment failures

**Custom Alerts (Prometheus + Alertmanager):**
```yaml
# alert.rules.yml
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        annotations:
          summary: "High error rate detected"
          
      - alert: SlowResponses
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        annotations:
          summary: "95th percentile response time > 2s"
```

---

### 4. Log Aggregation (Production)

**Tools:**
- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Grafana Loki**
- **Datadog**
- **New Relic**

**Example: Send logs to Datadog**
```python
# app/main.py
import logging
from datadog import initialize, statsd

initialize(api_key=os.getenv("DATADOG_API_KEY"))

@app.middleware("http")
async def log_to_datadog(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    # Send metrics
    statsd.increment("agent.requests", tags=[f"status:{response.status_code}"])
    statsd.histogram("agent.response_time", duration)
    
    return response
```

---

## 📊 Dashboard Examples

### Simple Dashboard (Terminal)

```bash
#!/bin/bash
# dashboard.sh

while true; do
    clear
    echo "=== AI Agent Dashboard ==="
    echo ""
    echo "Last 10 requests:"
    docker compose logs --tail 10 agent | grep '"status"' | \
      jq -r '"\(.ts) | \(.method) \(.path) | \(.status) | \(.ms)ms"'
    
    echo ""
    echo "Status codes (last 100):"
    docker compose logs --tail 100 agent | \
      grep '"status"' | \
      grep -o '"status":[0-9]*' | \
      cut -d: -f2 | \
      sort | uniq -c
    
    echo ""
    echo "Error rate:"
    TOTAL=$(docker compose logs --tail 100 agent | grep '"status"' | wc -l)
    ERRORS=$(docker compose logs --tail 100 agent | grep '"status":5' | wc -l)
    echo "$ERRORS / $TOTAL requests"
    
    sleep 5
done
```

**Run:**
```bash
chmod +x dashboard.sh
./dashboard.sh
```

---

## 🎯 Quick Reference

### Common Commands

```bash
# View logs
docker compose logs -f agent

# Find errors
docker compose logs agent | grep ERROR

# Find 500 errors
docker compose logs agent | grep '"status":500'

# Find 429 (rate limit)
docker compose logs agent | grep '"status":429'

# Find slow requests
docker compose logs agent | grep '{' | jq 'select(.ms > 2000)'

# Count by status
docker compose logs agent | grep '"status"' | cut -d: -f4 | cut -d, -f1 | sort | uniq -c

# Railway logs
railway logs

# Render logs
# Dashboard → Logs
```

### Log Patterns to Watch

| Pattern | Meaning | Action |
|---------|---------|--------|
| `"status":500` | Server error | Fix bug |
| `"status":429` | Rate limited | Normal or increase limit |
| `"status":401` | Unauthorized | Check API key |
| `"ms" > 2000` | Slow request | Optimize |
| `"redis_connection_failed"` | Redis down | Restart Redis |
| `"lvl":"ERROR"` | Any error | Investigate |

---

## 🆘 Troubleshooting

### Issue 1: No Logs Appearing

**Check:**
```bash
# Container running?
docker compose ps

# Logs exist?
docker compose logs agent

# Log level correct?
# Check DEBUG=true in .env.local
```

### Issue 2: Logs Too Verbose

**Fix:**
```bash
# Set log level to INFO
DEBUG=false

# Restart
docker compose restart agent
```

### Issue 3: Can't Parse JSON

**Fix:**
```bash
# Some logs are not JSON (startup messages)
# Filter only JSON lines
docker compose logs agent | grep '^{' | jq '.'
```

---

## 📚 Resources

- [Structured Logging Best Practices](https://www.loggly.com/ultimate-guide/python-logging-basics/)
- [Railway Logs Documentation](https://docs.railway.app/develop/logs)
- [Render Logs Documentation](https://render.com/docs/logs)
- [jq Tutorial](https://stedolan.github.io/jq/tutorial/)

---

**Happy Monitoring! 📊**

*Remember: Good logs = Easy debugging!*
