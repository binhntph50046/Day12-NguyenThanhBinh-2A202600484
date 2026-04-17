# 🚀 Lab 12 — Production-Ready AI Agent

> **AICB-P1 · VinUniversity 2026**  
> Kết hợp TẤT CẢ concepts về Deployment trong 1 project hoàn chỉnh

---

## 📋 Checklist Production-Ready

- [x] **Containerization**: Dockerfile multi-stage (< 500 MB)
- [x] **Orchestration**: docker-compose.yml (agent + redis)
- [x] **Health Checks**: `/health` (liveness) + `/ready` (readiness)
- [x] **Security**: API Key authentication + Security headers
- [x] **Rate Limiting**: 5 requests/phút per API key
- [x] **Cost Guard**: Budget protection
- [x] **Configuration**: 12-Factor App (environment variables)
- [x] **Logging**: Structured JSON logging
- [x] **Graceful Shutdown**: Handle SIGTERM properly
- [x] **Cloud Ready**: Railway + Render config files

---

## 🏗 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP + X-API-Key
       ▼
┌─────────────────────────────┐
│  FastAPI Agent              │
│  ├─ Auth Middleware         │
│  ├─ Rate Limiter (5/min)    │
│  ├─ Cost Guard              │
│  └─ Mock LLM                │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────┐
│  Redis          │
│  (Rate Limit)   │
└─────────────────┘
```

---

## 📁 Cấu Trúc Project

```
06-lab-complete/
├── app/
│   ├── main.py         # FastAPI app với tất cả middleware
│   └── config.py       # 12-factor config từ environment
├── utils/
│   └── mock_llm.py     # Mock LLM (không cần OpenAI key)
├── Dockerfile          # Multi-stage build
├── docker-compose.yml  # Agent + Redis stack
├── railway.toml        # Railway deployment config
├── render.yaml         # Render deployment config
├── .env.example        # Template cho environment variables
├── .dockerignore       # Exclude files khỏi Docker build
├── requirements.txt    # Python dependencies
└── README.md           # Bạn đang đọc đây!
```

---

## 🚦 Quick Start — Chạy Local

### Bước 1: Setup Environment

```bash
# Copy template và điền giá trị
cp .env.example .env.local

# Hoặc dùng default values (đủ cho testing)
```

### Bước 2: Chạy với Docker Compose

```bash
# Build và start tất cả services
docker compose up --build

# Hoặc chạy background
docker compose up -d
```

### Bước 3: Test Endpoints

```bash
# 1. Health check (không cần auth)
curl http://localhost:8000/health

# Response:
# {
#   "status": "ok",
#   "version": "1.0.0",
#   "uptime_seconds": 12.3,
#   ...
# }

# 2. Readiness check
curl http://localhost:8000/ready

# 3. Test API với authentication
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "What is deployment?"}'

# Response:
# {
#   "question": "What is deployment?",
#   "answer": "Deployment là quá trình đưa code từ máy bạn lên server...",
#   "model": "gpt-4o-mini",
#   "timestamp": "2026-04-17T10:30:00Z"
# }
```

### Bước 4: Test Rate Limiting

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

# Request thứ 6 sẽ nhận 429 Too Many Requests
```

---

## ☁️ Deploy lên Cloud

### Option 1: Railway (Khuyến nghị cho beginners)

**Ưu điểm:**
- ✅ Cực kỳ đơn giản (< 5 phút)
- ✅ Free $5 credit
- ✅ Tự động provision Redis
- ✅ HTTPS miễn phí

**Bước 1: Cài Railway CLI**

```bash
npm install -g @railway/cli
```

**Bước 2: Login**

```bash
railway login
```

**Bước 3: Initialize Project**

```bash
# Trong folder 06-lab-complete
railway init

# Chọn "Create new project"
# Đặt tên: "ai-agent-production"
```

**Bước 4: Add Redis**

```bash
railway add redis
```

**Bước 5: Set Environment Variables**

```bash
# Required variables
railway variables set AGENT_API_KEY=$(openssl rand -hex 16)
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false

# Optional: OpenAI key nếu muốn dùng LLM thật
railway variables set OPENAI_API_KEY=sk-...
```

**Bước 6: Deploy**

```bash
railway up
```

**Bước 7: Get Public URL**

```bash
railway domain

# Output: https://ai-agent-production.up.railway.app
```

**Bước 8: Test Production**

```bash
# Lấy API key đã set
API_KEY=$(railway variables get AGENT_API_KEY)

# Test
curl -X POST https://ai-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"question": "Hello from production!"}'
```

---

### Option 2: Render

**Ưu điểm:**
- ✅ Free tier 750 giờ/tháng
- ✅ Deploy từ GitHub (GitOps)
- ✅ Auto-deploy khi push code

**Bước 1: Push Code lên GitHub**

```bash
git init
git add .
git commit -m "Production-ready AI agent"
git remote add origin https://github.com/yourusername/ai-agent.git
git push -u origin main
```

**Bước 2: Render Dashboard**

1. Vào [render.com](https://render.com) → Sign up
2. Click **"New +"** → **"Blueprint"**
3. Connect GitHub repository
4. Render tự động đọc `render.yaml`

**Bước 3: Set Environment Variables**

Trong Render Dashboard:
- `AGENT_API_KEY`: Generate strong key
- `OPENAI_API_KEY`: (optional) OpenAI key
- `ENVIRONMENT`: production
- `DEBUG`: false

**Bước 4: Deploy**

Click **"Apply"** → Render sẽ:
- Provision Redis instance
- Build Docker image
- Deploy agent service
- Assign public URL

**Bước 5: Test**

```bash
curl https://your-agent.onrender.com/health
```

---

## 🔐 Security Best Practices

### 1. API Key Management

```bash
# ❌ KHÔNG làm thế này
AGENT_API_KEY=123456

# ✅ Generate strong key
openssl rand -hex 32
# Output: a3f5b2c8d9e1f4a7b6c3d8e2f9a1b4c7d5e8f2a9b3c6d1e4f7a2b5c8d9e1f4a7
```

### 2. Environment Variables

```bash
# ❌ KHÔNG commit .env.local
echo ".env.local" >> .gitignore

# ✅ Dùng .env.example làm template
cp .env.example .env.local
```

### 3. Rate Limiting

Hiện tại: **5 requests/phút** per API key

Tùy chỉnh trong `.env`:
```bash
RATE_LIMIT_PER_MINUTE=10  # Tăng lên 10 nếu cần
```

### 4. CORS Configuration

```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 📊 Monitoring & Debugging

### View Logs

**Docker Compose:**
```bash
docker compose logs -f agent
```

**Railway:**
```bash
railway logs
```

**Render:**
Dashboard → Logs tab

### Health Check

```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready
```

### Metrics (Protected Endpoint)

```bash
curl http://localhost:8000/metrics \
  -H "X-API-Key: your-api-key"

# Response:
# {
#   "uptime_seconds": 3600,
#   "total_requests": 150,
#   "error_count": 2,
#   "daily_cost_usd": 0.05,
#   "budget_used_pct": 1.0
# }
```

---

## 🐛 Troubleshooting

### Issue 1: Container không start

```bash
# Check logs
docker compose logs agent

# Common causes:
# - Port 8000 đã được dùng
# - Redis chưa ready
# - Environment variables thiếu
```

**Fix:**
```bash
# Thay port
PORT=8001 docker compose up
```

### Issue 2: Rate limit quá nhanh

```bash
# Tăng limit trong .env.local
RATE_LIMIT_PER_MINUTE=20

# Restart
docker compose restart agent
```

### Issue 3: Redis connection failed

```bash
# Check Redis đang chạy
docker compose ps redis

# Test connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

### Issue 4: 401 Unauthorized

```bash
# Check API key trong request
curl -v http://localhost:8000/ask \
  -H "X-API-Key: wrong-key" \
  ...

# Lấy đúng key từ .env.local
grep AGENT_API_KEY .env.local
```

---

## 🎯 Khác Biệt: Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Config** | Hardcoded | Environment variables |
| **Secrets** | Trong code | Encrypted, từ vault |
| **Logging** | `print()` | Structured JSON |
| **Error handling** | Stack trace | Generic message |
| **Debug mode** | `DEBUG=true` | `DEBUG=false` |
| **API docs** | `/docs` enabled | Disabled |
| **Health checks** | Không có | `/health`, `/ready` |
| **Shutdown** | Đột ngột | Graceful (30s timeout) |
| **Rate limiting** | Không có | 5 req/min |
| **HTTPS** | HTTP | HTTPS + Security headers |
| **User** | root | Non-root (agent:agent) |
| **Image size** | ~1 GB | < 500 MB |

---

## 📚 Concepts Quan Trọng

### 1. Multi-stage Docker Build

**Tại sao?**
- Stage 1 (builder): Compile dependencies (cần gcc, build tools)
- Stage 2 (runtime): Chỉ copy kết quả, không cần build tools
- **Kết quả**: Image nhỏ hơn 50-70%

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
COPY --from=builder /root/.local /home/agent/.local
```

### 2. Health Checks

**Liveness Probe** (`/health`):
- Container còn sống không?
- Fail → Platform restart container

**Readiness Probe** (`/ready`):
- Sẵn sàng nhận traffic không?
- Fail → Load balancer ngừng route traffic

### 3. Graceful Shutdown

```python
# Handle SIGTERM từ platform
signal.signal(signal.SIGTERM, shutdown_handler)

def shutdown_handler(signum, frame):
    # 1. Stop accepting new requests
    # 2. Finish current requests (timeout 30s)
    # 3. Close connections
    # 4. Exit
```

### 4. Rate Limiting Algorithm

**Sliding Window:**
```python
# Lưu timestamp của mỗi request
window = [t1, t2, t3, t4, t5]

# Xóa requests cũ hơn 60s
window = [t for t in window if t > now - 60]

# Check limit
if len(window) >= 5:
    raise HTTPException(429)
```

### 5. 12-Factor App

1. **Codebase**: 1 repo, nhiều deploys
2. **Dependencies**: Explicit (requirements.txt)
3. **Config**: Environment variables
4. **Backing services**: Redis as attached resource
5. **Build, release, run**: Tách biệt
6. **Processes**: Stateless
7. **Port binding**: Self-contained (uvicorn)
8. **Concurrency**: Scale via processes
9. **Disposability**: Fast startup, graceful shutdown
10. **Dev/prod parity**: Docker đảm bảo consistency
11. **Logs**: Stdout/stderr, structured JSON
12. **Admin processes**: Separate scripts

---

## 🎓 Bài Tập Nâng Cao

### Challenge 1: Thêm Conversation History

Lưu lịch sử chat trong Redis:

```python
import redis
r = redis.from_url(settings.REDIS_URL)

@app.post("/ask")
def ask(question: str, user_id: str):
    # Get history
    history = r.lrange(f"history:{user_id}", 0, 9)  # Last 10
    
    # Call LLM with context
    answer = llm_ask(question, history)
    
    # Save to history
    r.lpush(f"history:{user_id}", f"Q: {question}\nA: {answer}")
    r.ltrim(f"history:{user_id}", 0, 9)  # Keep only 10
    
    return {"answer": answer}
```

### Challenge 2: Streaming Responses

```python
from fastapi.responses import StreamingResponse

@app.post("/ask/stream")
async def ask_stream(question: str):
    def generate():
        for chunk in llm_ask_stream(question):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Challenge 3: Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 📖 Resources

- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

---

## ✅ Validation Checklist

Trước khi submit, check:

- [ ] `docker compose up` chạy thành công
- [ ] `/health` returns 200
- [ ] `/ready` returns 200
- [ ] `/ask` requires API key (401 without key)
- [ ] Rate limiting works (429 after 5 requests)
- [ ] Logs in JSON format
- [ ] Image size < 500 MB
- [ ] Deploy thành công lên Railway hoặc Render
- [ ] Public URL hoạt động

**Run validation script:**
```bash
python check_production_ready.py
```

---

## 🎉 Hoàn Thành!

Bạn đã xây dựng một **Production-Ready AI Agent** với:
- ✅ Security (API Key + Rate Limiting)
- ✅ Reliability (Health Checks + Graceful Shutdown)
- ✅ Scalability (Stateless + Docker)
- ✅ Observability (Structured Logging + Metrics)
- ✅ Cloud-Ready (Railway/Render deployment)

**Next Steps:**
1. Thêm monitoring (Prometheus + Grafana)
2. CI/CD pipeline (GitHub Actions)
3. Advanced scaling (Kubernetes)
4. Distributed tracing (OpenTelemetry)

---

**Happy Deploying! 🚀**

*Questions? Check TROUBLESHOOTING.md hoặc hỏi instructor.*
