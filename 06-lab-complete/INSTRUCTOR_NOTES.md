# 👨‍🏫 Instructor Notes — Lab Day 12

> **Internal document for instructors**

---

## 📋 Lab Overview

**Objective:** Sinh viên xây dựng một production-ready AI agent từ đầu

**Duration:** 3-4 giờ

**Difficulty:** Intermediate

**Prerequisites:**
- Python basics
- Basic understanding of APIs
- Docker installed
- Git basics

---

## 🎯 Learning Objectives

Sau khi hoàn thành lab, sinh viên sẽ:

1. ✅ Hiểu sự khác biệt giữa development và production
2. ✅ Biết cách containerize application với Docker
3. ✅ Deploy application lên cloud platform
4. ✅ Implement API security (authentication + rate limiting)
5. ✅ Thiết kế hệ thống scalable và reliable
6. ✅ Áp dụng 12-Factor App principles

---

## 📁 Project Structure

```
06-lab-complete/
├── app/
│   ├── main.py              # FastAPI application (500 lines)
│   └── config.py            # Configuration management (80 lines)
├── utils/
│   └── mock_llm.py          # Mock LLM (reused from parent)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Agent + Redis orchestration
├── .dockerignore            # Build optimization
├── .env.example             # Environment template
├── .env.local               # Local configuration (ready-to-use)
├── requirements.txt         # Python dependencies
├── railway.toml             # Railway deployment config
├── render.yaml              # Render deployment config
├── check_production_ready.py # Validation script (300 lines)
├── test_api.sh              # API testing script
├── README.md                # Main documentation (500 lines)
├── DEPLOYMENT_GUIDE.md      # Cloud deployment guide (800 lines)
├── QUICK_START.md           # 5-minute quick start (300 lines)
├── CONCEPTS.md              # Deep dive concepts (1000 lines)
└── SUMMARY.md               # Lab summary (400 lines)
```

**Total:** 18 files, ~4000 lines of code + documentation

---

## 🚀 Quick Start for Instructors

### Test Locally

```bash
cd 06-lab-complete

# Start services
docker compose up --build

# In another terminal, test
curl http://localhost:8000/health

# Run validation
python check_production_ready.py
```

### Deploy to Railway (Demo)

```bash
railway login
railway init
railway add redis
railway variables set AGENT_API_KEY=$(openssl rand -hex 16)
railway up
railway domain
```

---

## 📊 Grading Rubric

### Functionality (20 points)

- [ ] Agent responds to questions (5 pts)
- [ ] Health check works (5 pts)
- [ ] Readiness check works (5 pts)
- [ ] API endpoints functional (5 pts)

### Security (20 points)

- [ ] API Key authentication (7 pts)
- [ ] Rate limiting (5 req/min) (7 pts)
- [ ] Cost guard implemented (6 pts)

### Reliability (20 points)

- [ ] Health checks implemented (7 pts)
- [ ] Graceful shutdown (7 pts)
- [ ] Error handling (6 pts)

### Scalability (15 points)

- [ ] Stateless design (8 pts)
- [ ] Redis for shared state (7 pts)

### Docker (15 points)

- [ ] Multi-stage build (8 pts)
- [ ] Image size < 500 MB (7 pts)

### Deployment (10 points)

- [ ] Deployed to Railway/Render (5 pts)
- [ ] Public URL works (5 pts)

**Total: 100 points**

### Bonus Points (+10)

- [ ] JWT authentication (+3)
- [ ] Prometheus metrics (+3)
- [ ] CI/CD pipeline (+4)

---

## 🎓 Common Student Issues

### Issue 1: Docker Not Installed

**Symptom:** `docker: command not found`

**Solution:**
```bash
# macOS
brew install docker

# Windows
# Download Docker Desktop from docker.com

# Linux
sudo apt install docker.io docker-compose
```

### Issue 2: Port 8000 Already in Use

**Symptom:** `bind: address already in use`

**Solution:**
```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
PORT=8001 docker compose up
```

### Issue 3: Redis Connection Failed

**Symptom:** `redis.exceptions.ConnectionError`

**Solution:**
```bash
# Check Redis container
docker compose ps redis

# Restart Redis
docker compose restart redis

# Check logs
docker compose logs redis
```

### Issue 4: Rate Limiting Not Working

**Symptom:** Can make > 5 requests without 429

**Solution:**
- Check RATE_LIMIT_PER_MINUTE in .env.local
- Restart agent: `docker compose restart agent`
- Use same API key for all requests

### Issue 5: Railway Deployment Failed

**Symptom:** Build fails on Railway

**Solution:**
```bash
# Check Dockerfile exists
ls Dockerfile

# Check requirements.txt
ls requirements.txt

# Verify local build works
docker build -t test .

# Check Railway logs
railway logs
```

---

## 🧪 Testing Checklist

### Before Class

- [ ] Test `docker compose up` works
- [ ] Test all endpoints respond correctly
- [ ] Test rate limiting triggers
- [ ] Test authentication required
- [ ] Deploy to Railway (get demo URL)
- [ ] Test production URL works
- [ ] Run `check_production_ready.py` (should score 100%)

### During Class

- [ ] Demo local setup (5 min)
- [ ] Demo Docker build (5 min)
- [ ] Demo Railway deployment (10 min)
- [ ] Show logs and monitoring (5 min)
- [ ] Q&A (10 min)

### After Class

- [ ] Review student submissions
- [ ] Test each public URL
- [ ] Run validation script on each submission
- [ ] Provide feedback

---

## 📝 Submission Requirements

Students should submit:

1. **GitHub Repository URL**
   - All code committed
   - README.md complete
   - .env.example present (NOT .env.local)

2. **Public URL**
   - Railway or Render deployment
   - URL accessible
   - Health check returns 200

3. **API Key**
   - For instructor testing
   - Should be strong (not "123456")

4. **Screenshots** (3 required)
   - Dashboard showing deployment
   - Logs showing requests
   - `/health` endpoint response

5. **Validation Report**
   - Output of `check_production_ready.py`
   - Score should be > 90%

---

## 🎯 Key Concepts to Emphasize

### 1. Development vs Production

**Key Message:** "It works on my machine" is not enough

**Examples:**
- Hardcoded secrets → Environment variables
- `print()` → Structured JSON logging
- No health checks → `/health` and `/ready`
- Sudden shutdown → Graceful shutdown

### 2. 12-Factor App

**Key Message:** Build apps that are scalable and maintainable

**Focus on:**
- Config in environment (Factor 3)
- Stateless processes (Factor 6)
- Port binding (Factor 7)
- Disposability (Factor 9)

### 3. Docker Multi-stage Build

**Key Message:** Smaller images = faster deploys

**Demo:**
```bash
# Single-stage: 1.2 GB
docker build -f Dockerfile.single -t agent:single .

# Multi-stage: 450 MB
docker build -f Dockerfile -t agent:multi .

# Compare
docker images | grep agent
```

### 4. Health Checks

**Key Message:** Platform needs to know when to restart

**Demo:**
```bash
# Kill process inside container
docker compose exec agent kill 1

# Watch platform restart it
docker compose ps
```

### 5. Rate Limiting

**Key Message:** Protect your API from abuse

**Demo:**
```bash
# Make 6 requests quickly
for i in {1..6}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: key" \
    -d '{"question": "test"}'
done

# 6th request gets 429
```

---

## 💡 Teaching Tips

### Tip 1: Start with "Why"

Don't just show "how" to do things. Explain "why" it matters.

**Example:**
- ❌ "Add this health check endpoint"
- ✅ "Health checks let the platform know when to restart your app. Without them, a stuck process would stay stuck forever."

### Tip 2: Show Real Failures

Demo what happens when things go wrong:

```bash
# No health check → stuck process
# No graceful shutdown → dropped requests
# No rate limiting → API abuse
# No authentication → anyone can use
```

### Tip 3: Use Analogies

**Docker:** "Like a shipping container for code"
**Health check:** "Like a heartbeat monitor"
**Rate limiting:** "Like a bouncer at a club"
**Graceful shutdown:** "Like finishing your meal before leaving"

### Tip 4: Encourage Experimentation

```bash
# What happens if...
# - You remove the health check?
# - You increase rate limit to 100?
# - You disable authentication?
# - You make the image bigger?

# Let students try and see!
```

### Tip 5: Celebrate Small Wins

```bash
# ✅ Docker build successful
# ✅ Container started
# ✅ Health check passing
# ✅ API responding
# ✅ Deployed to cloud
# ✅ Public URL working

# Each step is progress!
```

---

## 🐛 Debugging Guide

### Check 1: Docker Running?

```bash
docker ps
# Should show containers

docker compose ps
# Should show agent and redis
```

### Check 2: Logs

```bash
# Agent logs
docker compose logs agent

# Redis logs
docker compose logs redis

# Follow logs
docker compose logs -f
```

### Check 3: Environment Variables

```bash
# Inside container
docker compose exec agent env | grep AGENT

# Check .env.local
cat .env.local
```

### Check 4: Network

```bash
# Test from inside container
docker compose exec agent curl http://localhost:8000/health

# Test from host
curl http://localhost:8000/health
```

### Check 5: Redis Connection

```bash
# Test Redis
docker compose exec redis redis-cli ping
# Should return: PONG

# Check connection from agent
docker compose exec agent python -c "import redis; r=redis.from_url('redis://redis:6379'); print(r.ping())"
```

---

## 📚 Additional Resources

### For Students

- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

### For Instructors

- [Teaching Docker](https://docker-curriculum.com/)
- [DevOps Roadmap](https://roadmap.sh/devops)
- [Production Best Practices](https://12factor.net/)

---

## 🎉 Success Criteria

A successful lab completion means:

1. ✅ Student understands dev vs prod differences
2. ✅ Student can containerize an application
3. ✅ Student can deploy to cloud
4. ✅ Student implements security best practices
5. ✅ Student designs for scalability
6. ✅ Student can debug production issues

**Most importantly:** Student feels confident deploying their own projects!

---

## 📊 Time Allocation

| Activity | Time | Notes |
|----------|------|-------|
| Introduction | 15 min | Explain objectives |
| Demo | 30 min | Show complete flow |
| Part 1: Local | 45 min | Docker setup |
| Break | 10 min | |
| Part 2: Security | 45 min | Auth + rate limiting |
| Part 3: Deploy | 45 min | Railway/Render |
| Break | 10 min | |
| Part 4: Testing | 30 min | Validation |
| Q&A | 20 min | |
| **Total** | **4 hours** | |

---

## 🆘 Emergency Contacts

**If students are stuck:**

1. Check TROUBLESHOOTING.md
2. Check QUICK_START.md
3. Run `check_production_ready.py`
4. Check logs: `docker compose logs`
5. Ask in Slack/Discord
6. Office hours

**If platform is down:**

- Railway down → Use Render
- Render down → Use Railway
- Both down → Use local Docker only

---

## ✅ Pre-class Checklist

- [ ] Test all code locally
- [ ] Deploy demo to Railway
- [ ] Deploy demo to Render
- [ ] Prepare slides
- [ ] Test projector/screen sharing
- [ ] Have backup plan (platform down)
- [ ] Print grading rubric
- [ ] Prepare Q&A answers

---

## 📝 Post-class TODO

- [ ] Collect submissions
- [ ] Test each public URL
- [ ] Run validation script
- [ ] Grade assignments
- [ ] Provide feedback
- [ ] Update lab based on feedback
- [ ] Share common issues with next class

---

**Good luck teaching! 🎓**

*Remember: The goal is not just to complete the lab, but to understand the concepts behind production deployment.*
