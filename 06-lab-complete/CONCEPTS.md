# 📚 Concepts — Hiểu Sâu về Production Deployment

> **AICB-P1 · VinUniversity**  
> Giải thích các concepts quan trọng trong bài Lab

---

## 🎯 Mục Lục

1. [Development vs Production](#development-vs-production)
2. [12-Factor App](#12-factor-app)
3. [Docker Multi-stage Build](#docker-multi-stage-build)
4. [Health Checks](#health-checks)
5. [Graceful Shutdown](#graceful-shutdown)
6. [Rate Limiting](#rate-limiting)
7. [API Authentication](#api-authentication)
8. [Structured Logging](#structured-logging)
9. [Stateless Design](#stateless-design)
10. [Security Best Practices](#security-best-practices)

---

## Development vs Production

### Tại Sao Cần Phân Biệt?

**Development:**
- Chạy trên laptop cá nhân
- Có thể restart bất cứ lúc nào
- Debug mode enabled
- Không cần bảo mật cao
- Chỉ 1 developer dùng

**Production:**
- Chạy trên cloud server
- Phải chạy 24/7
- Debug mode disabled
- Cần bảo mật cao
- Hàng nghìn users đồng thời

### So Sánh Chi Tiết

| Aspect | Development | Production | Tại Sao? |
|--------|-------------|------------|----------|
| **Config** | Hardcoded | Environment vars | Dễ thay đổi giữa môi trường |
| **Secrets** | Trong code | Encrypted vault | Bảo mật |
| **Logging** | `print()` | Structured JSON | Dễ parse và analyze |
| **Error messages** | Full stack trace | Generic message | Không leak info |
| **Debug mode** | `DEBUG=true` | `DEBUG=false` | Performance |
| **API docs** | `/docs` enabled | Disabled | Security |
| **HTTPS** | HTTP OK | HTTPS required | Encryption |
| **Rate limiting** | Không cần | Bắt buộc | Prevent abuse |
| **Health checks** | Không cần | Bắt buộc | Auto-restart |
| **Monitoring** | Không cần | Bắt buộc | Detect issues |

### Example: Config Management

**❌ Development (Bad for Production):**
```python
# Hardcoded
API_KEY = "secret-key-123"
PORT = 8000
DEBUG = True

app = FastAPI(debug=True)
```

**✅ Production (12-Factor):**
```python
# From environment
import os

API_KEY = os.getenv("API_KEY")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(debug=DEBUG)
```

---

## 12-Factor App

### Tại Sao Quan Trọng?

12-Factor App là methodology để build **scalable, maintainable** applications.

### 12 Principles

#### 1. Codebase
**One codebase tracked in version control, many deploys**

```bash
# Same code, different environments
git clone repo
git checkout main

# Deploy to dev
railway deploy --env dev

# Deploy to prod
railway deploy --env production
```

#### 2. Dependencies
**Explicitly declare and isolate dependencies**

```python
# requirements.txt
fastapi==0.115.0
uvicorn==0.30.0
redis==5.1.0

# Install
pip install -r requirements.txt
```

#### 3. Config
**Store config in environment variables**

```bash
# .env.local
PORT=8000
REDIS_URL=redis://localhost:6379

# .env.production
PORT=8000
REDIS_URL=redis://prod-redis:6379
```

#### 4. Backing Services
**Treat backing services as attached resources**

```python
# Redis là backing service
# Có thể swap giữa local và cloud
redis_url = os.getenv("REDIS_URL")
r = redis.from_url(redis_url)
```

#### 5. Build, Release, Run
**Strictly separate build and run stages**

```bash
# Build
docker build -t agent:v1.0 .

# Release
docker tag agent:v1.0 registry.com/agent:v1.0
docker push registry.com/agent:v1.0

# Run
docker run registry.com/agent:v1.0
```

#### 6. Processes
**Execute the app as one or more stateless processes**

```python
# ❌ State trong memory
conversation_history = {}  # Lost khi restart!

# ✅ State trong Redis
r.set(f"history:{user_id}", json.dumps(history))
```

#### 7. Port Binding
**Export services via port binding**

```python
# Self-contained, không cần Apache/Nginx
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 8. Concurrency
**Scale out via the process model**

```bash
# Scale horizontally
docker compose up --scale agent=3
```

#### 9. Disposability
**Maximize robustness with fast startup and graceful shutdown**

```python
# Fast startup
@app.on_event("startup")
async def startup():
    # Minimal initialization
    pass

# Graceful shutdown
signal.signal(signal.SIGTERM, shutdown_handler)
```

#### 10. Dev/Prod Parity
**Keep development, staging, and production as similar as possible**

```bash
# Same Docker image everywhere
docker build -t agent .

# Dev
docker run agent

# Prod
docker run agent
```

#### 11. Logs
**Treat logs as event streams**

```python
# Write to stdout, platform handles collection
logger.info(json.dumps({
    "event": "request",
    "method": "POST",
    "status": 200
}))
```

#### 12. Admin Processes
**Run admin/management tasks as one-off processes**

```bash
# Database migration
docker compose run agent python migrate.py

# One-time script
docker compose run agent python cleanup.py
```

---

## Docker Multi-stage Build

### Tại Sao Cần?

**Problem:** Docker image quá lớn (> 1 GB)
- Chứa build tools (gcc, make, etc.)
- Chứa source code không cần thiết
- Slow deployment

**Solution:** Multi-stage build
- Stage 1: Build dependencies
- Stage 2: Copy chỉ kết quả
- **Result:** Image < 500 MB

### Example

**❌ Single-stage (1.2 GB):**
```dockerfile
FROM python:3.11

# Install build tools
RUN apt-get update && apt-get install -y gcc make

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY . .

CMD ["uvicorn", "app.main:app"]
```

**✅ Multi-stage (450 MB):**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Copy ONLY installed packages
COPY --from=builder /root/.local /home/agent/.local

# Copy app
COPY app/ ./app/

CMD ["uvicorn", "app.main:app"]
```

### Kết Quả

```bash
# Build
docker build -t agent .

# Check size
docker images agent
# REPOSITORY   TAG       SIZE
# agent        latest    450MB  # ✅ < 500 MB
```

---

## Health Checks

### Tại Sao Cần?

Platform (Railway, Render, K8s) cần biết:
1. **Liveness:** Container còn sống không?
2. **Readiness:** Sẵn sàng nhận traffic không?

### Liveness Probe

**Mục đích:** Detect khi container bị "stuck"

```python
@app.get("/health")
def health():
    """
    Liveness probe — Platform restarts nếu fail
    
    Check:
    - Process còn chạy không?
    - Memory không bị leak?
    """
    return {"status": "ok"}
```

**Platform config:**
```yaml
# Kubernetes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3  # Restart sau 3 lần fail
```

### Readiness Probe

**Mục đích:** Detect khi container chưa sẵn sàng

```python
@app.get("/ready")
def ready():
    """
    Readiness probe — Load balancer ngừng route nếu fail
    
    Check:
    - Database connected?
    - Redis connected?
    - Dependencies ready?
    """
    try:
        # Check Redis
        r.ping()
        return {"ready": True}
    except:
        raise HTTPException(503, "Not ready")
```

**Platform config:**
```yaml
# Kubernetes
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 2  # Stop routing sau 2 lần fail
```

### Khác Biệt

| Aspect | Liveness | Readiness |
|--------|----------|-----------|
| **Question** | Còn sống không? | Sẵn sàng không? |
| **Action if fail** | Restart container | Stop routing traffic |
| **Check** | Process health | Dependencies ready |
| **Example fail** | Deadlock, OOM | DB down, Redis down |

---

## Graceful Shutdown

### Tại Sao Cần?

**Problem:** Platform gửi SIGTERM → Container die ngay lập tức
- Requests đang xử lý bị drop
- Data loss
- Bad user experience

**Solution:** Graceful shutdown
1. Stop accepting new requests
2. Finish current requests (timeout 30s)
3. Close connections
4. Exit

### Implementation

```python
import signal
import sys

_is_shutting_down = False

def shutdown_handler(signum, frame):
    """Handle SIGTERM from platform"""
    global _is_shutting_down
    
    logger.info("Received SIGTERM, shutting down gracefully...")
    _is_shutting_down = True
    
    # Wait for current requests to finish (max 30s)
    time.sleep(30)
    
    # Close connections
    r.close()  # Redis
    db.close()  # Database
    
    logger.info("Shutdown complete")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)

@app.middleware("http")
async def reject_during_shutdown(request, call_next):
    if _is_shutting_down:
        return Response("Service shutting down", status_code=503)
    return await call_next(request)
```

### Test

```bash
# Start container
docker run --name agent agent

# Send request
curl http://localhost:8000/ask &

# Immediately send SIGTERM
docker kill --signal=SIGTERM agent

# Request vẫn hoàn thành!
```

---

## Rate Limiting

### Tại Sao Cần?

**Problem:** User abuse API
- Spam requests → Hết tiền OpenAI
- DDoS attack
- Unfair usage

**Solution:** Rate limiting
- Giới hạn X requests/phút per user
- Return 429 Too Many Requests khi vượt

### Algorithms

#### 1. Fixed Window

```python
# Simple nhưng có "burst" problem
def check_rate_limit(user_id):
    minute = int(time.time() / 60)
    key = f"rate:{user_id}:{minute}"
    
    count = r.incr(key)
    r.expire(key, 60)
    
    if count > 5:
        raise HTTPException(429)
```

**Problem:** Burst at window boundary
```
Minute 1: 5 requests at 0:59
Minute 2: 5 requests at 1:00
→ 10 requests trong 1 giây!
```

#### 2. Sliding Window (Better)

```python
def check_rate_limit(user_id):
    now = time.time()
    key = f"rate:{user_id}"
    
    # Remove old requests
    r.zremrangebyscore(key, 0, now - 60)
    
    # Count requests in last 60s
    count = r.zcard(key)
    
    if count >= 5:
        raise HTTPException(429)
    
    # Add current request
    r.zadd(key, {str(now): now})
    r.expire(key, 60)
```

**Advantage:** Smooth limiting, no burst

#### 3. Token Bucket (Advanced)

```python
def check_rate_limit(user_id):
    key = f"tokens:{user_id}"
    
    # Get current tokens
    tokens = float(r.get(key) or 5)
    last_refill = float(r.get(f"{key}:time") or time.time())
    
    # Refill tokens (1 token/12 seconds = 5/minute)
    now = time.time()
    elapsed = now - last_refill
    tokens = min(5, tokens + elapsed / 12)
    
    if tokens < 1:
        raise HTTPException(429)
    
    # Consume 1 token
    r.set(key, tokens - 1)
    r.set(f"{key}:time", now)
```

**Advantage:** Allow bursts, smooth over time

---

## API Authentication

### Tại Sao Cần?

**Problem:** Public API → Anyone can call → Hết tiền

**Solution:** Authentication
- API Key: Simple, good for server-to-server
- JWT: Complex, good for user sessions

### API Key

```python
from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str = Header(...)):
    """
    Check API key trong header: X-API-Key
    """
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(401, "Invalid API key")
    return x_api_key

@app.post("/ask")
def ask(question: str, _key: str = Depends(verify_api_key)):
    # Only reachable with valid key
    return llm_ask(question)
```

**Usage:**
```bash
curl -H "X-API-Key: secret-key-123" http://api.com/ask
```

### JWT (Advanced)

```python
import jwt
from datetime import datetime, timedelta

def create_token(user_id: str) -> str:
    """Generate JWT token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> str:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

**Usage:**
```bash
# 1. Get token
TOKEN=$(curl -X POST http://api.com/token \
  -d '{"username":"admin","password":"secret"}' | jq -r .token)

# 2. Use token
curl -H "Authorization: Bearer $TOKEN" http://api.com/ask
```

---

## Structured Logging

### Tại Sao Cần?

**Problem:** `print()` logs khó parse
```
Request received
Processing...
Done in 123ms
```

**Solution:** Structured JSON logs
```json
{"ts":"2026-04-17T10:30:00Z","event":"request","method":"POST","path":"/ask","status":200,"ms":123}
```

### Implementation

```python
import logging
import json

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}'
)

logger = logging.getLogger(__name__)

# Log structured data
logger.info(json.dumps({
    "event": "request",
    "method": request.method,
    "path": request.url.path,
    "status": response.status_code,
    "duration_ms": duration
}))
```

### Benefits

1. **Easy to parse:**
```bash
# Filter errors
cat logs.json | jq 'select(.lvl=="ERROR")'

# Average response time
cat logs.json | jq '.ms' | awk '{sum+=$1} END {print sum/NR}'
```

2. **Easy to search:**
```bash
# Find slow requests
cat logs.json | jq 'select(.ms > 1000)'
```

3. **Easy to aggregate:**
```python
# Send to monitoring system
for log in logs:
    prometheus.counter("requests_total").inc()
    prometheus.histogram("request_duration").observe(log["ms"])
```

---

## Stateless Design

### Tại Sao Cần?

**Problem:** State trong memory → Không scale được

```python
# ❌ State trong memory
conversation_history = {}

@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])
    # ...
```

**Vấn đề:**
- Scale to 3 instances → Mỗi instance có memory riêng
- User request đến instance 1 → History ở instance 1
- Next request đến instance 2 → Không có history!

**Solution:** State trong Redis (shared storage)

```python
# ✅ State trong Redis
@app.post("/ask")
def ask(user_id: str, question: str):
    history = r.lrange(f"history:{user_id}", 0, 9)
    # ...
    r.lpush(f"history:{user_id}", message)
```

### Test Stateless

```bash
# Start 3 instances
docker compose up --scale agent=3

# Request 1 → Instance 1
curl http://localhost/ask -d '{"user_id":"user1","question":"Hello"}'

# Request 2 → Instance 2 (load balanced)
curl http://localhost/ask -d '{"user_id":"user1","question":"Continue"}'

# History vẫn có! (vì lưu trong Redis)
```

---

## Security Best Practices

### 1. Never Hardcode Secrets

**❌ Bad:**
```python
API_KEY = "sk-1234567890abcdef"
```

**✅ Good:**
```python
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not set")
```

### 2. Use Strong Keys

```bash
# ❌ Weak
API_KEY=123456

# ✅ Strong
API_KEY=$(openssl rand -hex 32)
# a3f5b2c8d9e1f4a7b6c3d8e2f9a1b4c7d5e8f2a9b3c6d1e4f7a2b5c8d9e1f4a7
```

### 3. Run as Non-root

```dockerfile
# ❌ Run as root
USER root

# ✅ Run as non-root
RUN useradd -r agent
USER agent
```

### 4. Security Headers

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 5. Input Validation

```python
from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    
@app.post("/ask")
def ask(body: AskRequest):  # Auto-validated
    # question guaranteed to be 1-2000 chars
    pass
```

### 6. Rate Limiting

```python
# Prevent abuse
@app.post("/ask")
def ask(_rate_limit: None = Depends(check_rate_limit)):
    pass
```

### 7. HTTPS Only

```python
# Redirect HTTP to HTTPS
@app.middleware("http")
async def https_redirect(request, call_next):
    if request.url.scheme == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url)
    return await call_next(request)
```

---

## 🎓 Summary

| Concept | Tại Sao Quan Trọng | Implementation |
|---------|-------------------|----------------|
| **12-Factor** | Scalable, maintainable | Environment vars, stateless |
| **Multi-stage** | Small image size | Dockerfile with 2 stages |
| **Health checks** | Auto-restart | `/health`, `/ready` endpoints |
| **Graceful shutdown** | No dropped requests | Handle SIGTERM |
| **Rate limiting** | Prevent abuse | Sliding window algorithm |
| **Authentication** | Security | API Key or JWT |
| **Structured logging** | Easy to parse | JSON format |
| **Stateless** | Horizontal scaling | State in Redis |
| **Security** | Protect users | Non-root, HTTPS, validation |

---

**Hiểu concepts → Build better systems! 🚀**
