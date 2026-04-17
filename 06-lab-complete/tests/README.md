# 🧪 Test Suite — Production AI Agent

> **Comprehensive testing for production-ready AI Agent**

---

## 📋 Test Files

### 1. `test_agent.py` — Main Test Suite

Comprehensive test suite covering:
- ✅ Basic functionality (health, readiness, API)
- ✅ Security (authentication, authorization)
- ✅ Validation (input validation, edge cases)
- ✅ Rate limiting (5 requests/minute)
- ✅ Performance (response time)
- ✅ Stress testing (concurrent requests)

**Usage:**
```bash
# Test local
python tests/test_agent.py

# Test production
python tests/test_agent.py --url https://my-agent.up.railway.app

# Include stress tests
python tests/test_agent.py --stress

# Custom API key
python tests/test_agent.py --api-key your-key-here
```

**Expected output:**
```
================================
  PRODUCTION AGENT TEST SUITE
================================

Testing: http://localhost:8000
API Key: dev-key-ch...

🔍 BASIC TESTS
✓ Health Check ................................. PASS
✓ Readiness Check .............................. PASS
✓ Valid API Request ............................ PASS

🔐 SECURITY TESTS
✓ Missing API Key .............................. PASS
✓ Invalid API Key .............................. PASS

...

📊 TEST SUMMARY
Total tests: 13
Passed: 13
Failed: 0
Warnings: 0

Success rate: 100.0%

🎉 EXCELLENT! Production ready!
```

---

### 2. `test_stateless.py` — Stateless Design Test

Tests if agent is truly stateless by verifying Redis persistence across restarts.

**Usage:**
```bash
# Step 1: Create session
python tests/test_stateless.py --step 1

# Step 2: Restart container
docker compose restart agent

# Step 3: Verify session
python tests/test_stateless.py --step 3 --session <session-id>
```

**What it tests:**
- ✅ Session data stored in Redis
- ✅ Rate limiting state preserved
- ✅ Agent works after restart
- ✅ No data loss

---

### 3. `LOG_MONITORING_GUIDE.md` — Log Analysis Guide

Comprehensive guide for reading and analyzing logs:
- 📊 Log structure (JSON format)
- 🔍 Finding errors (500, 429, 401)
- 📈 Performance monitoring
- 🚨 Setting up alerts
- 🛠️ Troubleshooting

**Topics covered:**
- Local logs (Docker Compose)
- Railway logs (CLI + Dashboard)
- Render logs (Dashboard)
- Log parsing with `jq`
- Error patterns
- Monitoring scripts

---

## 🚀 Quick Start

### Install Dependencies

```bash
pip install requests redis
```

### Run All Tests

```bash
# Make sure agent is running
docker compose up -d

# Run tests
python tests/test_agent.py

# Run with stress tests
python tests/test_agent.py --stress
```

### Test Production

```bash
# Get your production URL
PROD_URL="https://my-agent.up.railway.app"

# Get your API key
API_KEY="your-production-api-key"

# Run tests
python tests/test_agent.py --url $PROD_URL --api-key $API_KEY
```

---

## 📊 Test Coverage

### Functional Tests (3)
- [x] Health check endpoint
- [x] Readiness check endpoint
- [x] Valid API request

### Security Tests (2)
- [x] Missing API key (401)
- [x] Invalid API key (401)

### Validation Tests (2)
- [x] Empty question (422)
- [x] Missing question field (422)

### Edge Cases (3)
- [x] Very long question (2500+ chars)
- [x] Special characters (XSS, Unicode)
- [x] SQL injection attempt

### Rate Limiting (1)
- [x] Rate limit enforcement (5 req/min)

### Stateless Design (1)
- [x] Independent requests

### Stress Tests (2) — Optional
- [x] Concurrent requests (20 simultaneous)
- [x] Response time (average < 2s)

**Total: 14 test cases**

---

## 🎯 Test Scenarios

### Scenario 1: Positive Tests (Happy Path)

```bash
# All these should return 200 OK
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "Hello"}'
```

### Scenario 2: Negative Tests (Error Handling)

```bash
# Missing API key → 401
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Invalid API key → 401
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"question": "Hello"}'

# Empty question → 422
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": ""}'
```

### Scenario 3: Rate Limiting

```bash
# Make 6 requests quickly
for i in {1..6}; do
  curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: dev-key-change-me-in-production" \
    -d "{\"question\": \"Test $i\"}"
  echo ""
done

# 6th request should return 429
```

### Scenario 4: Edge Cases

```bash
# Very long question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "'$(python -c 'print("A"*2500)')'"}'

# Special characters
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "<script>alert(\"xss\")</script>"}'

# SQL injection
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "'\'' OR 1=1; DROP TABLE users; --"}'
```

---

## 🐛 Debugging Failed Tests

### Test Failed: Health Check

**Possible causes:**
- Agent not running
- Wrong URL
- Network issue

**Fix:**
```bash
# Check if agent is running
docker compose ps

# Check logs
docker compose logs agent

# Restart agent
docker compose restart agent
```

### Test Failed: Authentication

**Possible causes:**
- Wrong API key
- API key not set in environment

**Fix:**
```bash
# Check API key in .env.local
grep AGENT_API_KEY .env.local

# Use correct key in test
python tests/test_agent.py --api-key <correct-key>
```

### Test Failed: Rate Limiting

**Possible causes:**
- Rate limit not configured
- Redis not running

**Fix:**
```bash
# Check Redis
docker compose ps redis

# Check rate limit setting
grep RATE_LIMIT_PER_MINUTE .env.local

# Restart agent
docker compose restart agent
```

---

## 📈 Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| Health check | < 100ms | < 500ms |
| API request | < 500ms | < 2s |
| Concurrent (10) | All succeed | < 2 failures |
| Rate limit | Triggers at 6th | Triggers at 5-7th |

### Measure Performance

```bash
# Response time
time curl http://localhost:8000/health

# Average over 10 requests
for i in {1..10}; do
  time curl -s http://localhost:8000/health > /dev/null
done 2>&1 | grep real
```

---

## 🎓 Best Practices

### 1. Test Locally First

Always test locally before testing production:
```bash
# Start local
docker compose up -d

# Test local
python tests/test_agent.py

# If pass → Test production
python tests/test_agent.py --url https://prod-url
```

### 2. Use Correct API Key

```bash
# Local
API_KEY="dev-key-change-me-in-production"

# Production (from Railway)
API_KEY=$(railway variables get AGENT_API_KEY)

# Production (from Render)
# Get from Dashboard → Environment
```

### 3. Wait Between Tests

Rate limiting can affect tests. Wait 60s between test runs:
```bash
python tests/test_agent.py
sleep 60
python tests/test_agent.py
```

### 4. Check Logs

Always check logs when tests fail:
```bash
# Local
docker compose logs agent

# Railway
railway logs

# Render
# Dashboard → Logs
```

---

## 🆘 Troubleshooting

### Issue 1: Connection Refused

**Error:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Fix:**
```bash
# Check if agent is running
docker compose ps

# Start agent
docker compose up -d

# Check port
curl http://localhost:8000/health
```

### Issue 2: Timeout

**Error:**
```
requests.exceptions.Timeout: Request timeout
```

**Fix:**
```bash
# Check if agent is responding
docker compose logs agent

# Restart agent
docker compose restart agent

# Increase timeout in test
# Edit test_agent.py: timeout=30
```

### Issue 3: Rate Limited During Tests

**Error:**
```
429 Too Many Requests
```

**Fix:**
```bash
# Wait 60 seconds
sleep 60

# Or increase rate limit temporarily
RATE_LIMIT_PER_MINUTE=100 docker compose up -d
```

---

## 📚 Resources

- [requests Documentation](https://requests.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [API Testing Best Practices](https://www.postman.com/api-testing/)

---

## ✅ Pre-deployment Checklist

Before deploying to production, ensure:

- [ ] All tests pass locally
- [ ] Rate limiting works (429 after 5 requests)
- [ ] Authentication required (401 without key)
- [ ] Health checks return 200
- [ ] No 500 errors in logs
- [ ] Response time < 2s
- [ ] Stateless test passes

**Run full test suite:**
```bash
python tests/test_agent.py --stress
```

**Expected:** 100% pass rate

---

**Happy Testing! 🧪**

*Good tests = Confident deployments!*
