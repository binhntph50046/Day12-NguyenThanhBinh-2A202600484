# ⚡ Quick Start — 5 Phút Chạy Production Agent

> **Dành cho sinh viên AICB-P1 muốn test nhanh**

---

## 🎯 Mục Tiêu

Trong 5 phút, bạn sẽ có:
- ✅ Agent chạy local với Docker
- ✅ Redis cho rate limiting
- ✅ API endpoint hoạt động
- ✅ Health checks working

---

## 📋 Prerequisites

```bash
# Check Docker installed
docker --version
# Should show: Docker version 20.x.x or higher

# Check Docker Compose installed
docker compose version
# Should show: Docker Compose version v2.x.x or higher
```

**Chưa có Docker?**
- macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: `sudo apt install docker.io docker-compose`

---

## 🚀 3 Bước Chạy

### Bước 1: Clone/Navigate to Project

```bash
cd 06-lab-complete
```

### Bước 2: Start Services

```bash
docker compose up --build
```

**Output bạn sẽ thấy:**
```
[+] Building 45.2s (15/15) FINISHED
[+] Running 2/2
 ✔ Container redis    Started
 ✔ Container agent    Started

agent  | {"ts":"2026-04-17 10:30:00","lvl":"INFO","msg":"startup"}
agent  | {"ts":"2026-04-17 10:30:00","lvl":"INFO","msg":"ready"}
```

**Chờ đến khi thấy "ready"** → Agent đã sẵn sàng!

### Bước 3: Test API

**Mở terminal mới** (giữ nguyên terminal cũ):

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Expected:
# {
#   "status": "ok",
#   "version": "1.0.0",
#   "uptime_seconds": 5.2,
#   ...
# }

# Test 2: Ask agent (với API key)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "What is deployment?"}'

# Expected:
# {
#   "question": "What is deployment?",
#   "answer": "Deployment là quá trình đưa code từ máy bạn lên server...",
#   "model": "gpt-4o-mini",
#   "timestamp": "2026-04-17T10:30:00Z"
# }
```

**🎉 Nếu thấy response → SUCCESS!**

---

## 🧪 Test Các Features

### Test 1: Authentication

```bash
# ❌ Không có API key → 401
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'

# Expected: 401 Unauthorized
```

### Test 2: Rate Limiting

```bash
# Gọi 6 lần liên tục (limit là 5/phút)
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: dev-key-change-me-in-production" \
    -d "{\"question\": \"Test $i\"}"
  echo -e "\n"
done

# Request 6 sẽ nhận: 429 Too Many Requests
```

### Test 3: Health Checks

```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready
```

### Test 4: Metrics

```bash
curl http://localhost:8000/metrics \
  -H "X-API-Key: dev-key-change-me-in-production"

# Shows:
# - uptime_seconds
# - total_requests
# - error_count
# - daily_cost_usd
```

---

## 🔍 View Logs

```bash
# View logs (real-time)
docker compose logs -f agent

# View Redis logs
docker compose logs -f redis

# View all logs
docker compose logs -f
```

**Expected log format (JSON):**
```json
{"ts":"2026-04-17 10:30:00","lvl":"INFO","msg":"startup"}
{"ts":"2026-04-17 10:30:05","lvl":"INFO","msg":"request","method":"POST","path":"/ask","status":200,"ms":123.4}
```

---

## 🛑 Stop Services

```bash
# Stop (Ctrl+C trong terminal đang chạy)
# Hoặc:
docker compose down

# Stop và xóa volumes (Redis data)
docker compose down -v
```

---

## 🐛 Troubleshooting

### Issue 1: Port 8000 đã được dùng

**Error:**
```
Error: bind: address already in use
```

**Fix:**
```bash
# Option 1: Kill process đang dùng port 8000
lsof -ti:8000 | xargs kill -9

# Option 2: Thay port
PORT=8001 docker compose up
```

### Issue 2: Docker daemon không chạy

**Error:**
```
Cannot connect to the Docker daemon
```

**Fix:**
- macOS/Windows: Mở Docker Desktop
- Linux: `sudo systemctl start docker`

### Issue 3: Redis connection failed

**Error:**
```
redis.exceptions.ConnectionError
```

**Fix:**
```bash
# Check Redis container
docker compose ps redis

# Restart Redis
docker compose restart redis
```

### Issue 4: Build failed

**Error:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete
```

**Fix:**
```bash
# Clean build
docker compose down
docker compose build --no-cache
docker compose up
```

---

## 📊 Validate Production Readiness

```bash
# Run checker script
python check_production_ready.py

# Expected output:
# ✓ Dockerfile (multi-stage) .................... PASS
# ✓ .dockerignore ............................... PASS
# ✓ Health endpoint (/health) ................... PASS
# ...
# Score: 95.0%
# 🎉 EXCELLENT! Production ready!
```

---

## 🚀 Next Steps

### 1. Customize Configuration

```bash
# Edit .env.local
nano .env.local

# Change:
RATE_LIMIT_PER_MINUTE=10  # Tăng limit
DAILY_BUDGET_USD=10.0     # Tăng budget

# Restart
docker compose restart agent
```

### 2. Add OpenAI Key (Optional)

```bash
# Edit .env.local
OPENAI_API_KEY=sk-your-real-key

# Restart
docker compose restart agent

# Now agent sẽ dùng OpenAI thật thay vì Mock LLM
```

### 3. Deploy to Cloud

```bash
# Railway (easiest)
npm install -g @railway/cli
railway login
railway init
railway up

# Render (GitOps)
git push origin main
# Then connect repo in Render dashboard

# See DEPLOYMENT_GUIDE.md for details
```

---

## 📚 Files Quan Trọng

```
06-lab-complete/
├── app/main.py              # FastAPI app logic
├── app/config.py            # Configuration management
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Orchestration
├── .env.local               # Local environment vars
├── requirements.txt         # Python dependencies
├── README.md                # Full documentation
├── DEPLOYMENT_GUIDE.md      # Deploy to cloud
└── check_production_ready.py # Validation script
```

---

## 🎯 Checklist

Trước khi submit assignment:

- [ ] `docker compose up` chạy thành công
- [ ] `/health` returns 200
- [ ] `/ready` returns 200
- [ ] `/ask` requires API key (401 without)
- [ ] Rate limiting works (429 after 5 requests)
- [ ] Logs in JSON format
- [ ] `check_production_ready.py` score > 90%
- [ ] Deploy lên Railway hoặc Render
- [ ] Public URL hoạt động

---

## 💡 Tips

### Tip 1: Use Postman

Import collection:
```json
{
  "info": {"name": "AI Agent"},
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    },
    {
      "name": "Ask Agent",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/ask",
        "header": [
          {"key": "Content-Type", "value": "application/json"},
          {"key": "X-API-Key", "value": "dev-key-change-me-in-production"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"question\": \"What is Docker?\"}"
        }
      }
    }
  ]
}
```

### Tip 2: Watch Logs

```bash
# Terminal 1: Run services
docker compose up

# Terminal 2: Watch logs
watch -n 1 'docker compose logs --tail 20 agent'

# Terminal 3: Make requests
curl http://localhost:8000/ask ...
```

### Tip 3: Debug Container

```bash
# Enter container shell
docker compose exec agent /bin/sh

# Check Python version
python --version

# Check packages
pip list

# Check environment
env | grep AGENT
```

---

## 🆘 Need Help?

1. **Check logs:** `docker compose logs agent`
2. **Check README.md:** Full documentation
3. **Check TROUBLESHOOTING.md:** Common issues
4. **Ask instructor:** Office hours or Slack

---

**Chúc bạn thành công! 🎉**

*Time to complete: ~5 minutes*  
*Difficulty: ⭐ Easy*
