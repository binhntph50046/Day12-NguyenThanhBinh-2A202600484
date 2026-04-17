# 🚀 Hướng Dẫn Deploy Chi Tiết

> **Dành cho sinh viên AICB-P1 · VinUniversity**

---

## 📋 Mục Lục

1. [Chuẩn Bị](#chuẩn-bị)
2. [Deploy Railway](#deploy-railway)
3. [Deploy Render](#deploy-render)
4. [Deploy Google Cloud Run](#deploy-google-cloud-run-nâng-cao)
5. [So Sánh Platforms](#so-sánh-platforms)
6. [Troubleshooting](#troubleshooting)

---

## Chuẩn Bị

### Checklist Trước Khi Deploy

- [ ] Code đã test thành công local (`docker compose up`)
- [ ] `.env.example` đã có đầy đủ variables
- [ ] `.dockerignore` đã exclude files không cần thiết
- [ ] `Dockerfile` build thành công
- [ ] Git repository đã được tạo (nếu dùng Render)

### Test Local Lần Cuối

```bash
# Build và run
docker compose up --build

# Test health
curl http://localhost:8000/health

# Test API
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -d '{"question": "Test deployment"}'

# Nếu OK → Ready to deploy!
```

---

## Deploy Railway

### Tại Sao Chọn Railway?

✅ **Ưu điểm:**
- Cực kỳ đơn giản (< 5 phút)
- Free $5 credit (đủ chạy 1-2 tháng)
- Tự động provision Redis
- HTTPS miễn phí
- CLI mạnh mẽ

❌ **Nhược điểm:**
- Free tier giới hạn
- Không có region Việt Nam (latency cao hơn)

---

### Bước 1: Cài Đặt Railway CLI

**macOS/Linux:**
```bash
npm install -g @railway/cli

# Hoặc dùng Homebrew
brew install railway
```

**Windows:**
```bash
npm install -g @railway/cli
```

**Verify installation:**
```bash
railway --version
```

---

### Bước 2: Login Railway

```bash
railway login
```

Browser sẽ mở → Login với GitHub/Google

**Verify:**
```bash
railway whoami
```

---

### Bước 3: Initialize Project

```bash
# Trong folder 06-lab-complete
cd 06-lab-complete

# Initialize
railway init

# Chọn:
# - "Create new project"
# - Project name: "ai-agent-production"
# - Environment: "production"
```

**Output:**
```
✓ Created project ai-agent-production
✓ Linked to production environment
```

---

### Bước 4: Add Redis Service

```bash
railway add redis
```

Railway sẽ:
- Provision Redis instance
- Tự động set `REDIS_URL` environment variable

**Verify:**
```bash
railway variables
# Should see REDIS_URL=redis://...
```

---

### Bước 5: Set Environment Variables

```bash
# Generate strong API key
API_KEY=$(openssl rand -hex 16)
echo "Your API Key: $API_KEY"

# Set variables
railway variables set AGENT_API_KEY=$API_KEY
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PORT=8000
railway variables set RATE_LIMIT_PER_MINUTE=5

# Optional: OpenAI key nếu muốn dùng LLM thật
railway variables set OPENAI_API_KEY=sk-...
```

**Verify:**
```bash
railway variables
```

---

### Bước 6: Deploy

```bash
railway up
```

Railway sẽ:
1. Upload code
2. Build Docker image
3. Deploy container
4. Start services

**Output:**
```
✓ Build successful
✓ Deployment live
✓ https://ai-agent-production-xxx.up.railway.app
```

---

### Bước 7: Get Public URL

```bash
railway domain
```

**Output:**
```
https://ai-agent-production-xxx.up.railway.app
```

Copy URL này!

---

### Bước 8: Test Production

```bash
# Set variables
RAILWAY_URL="https://ai-agent-production-xxx.up.railway.app"
API_KEY=$(railway variables get AGENT_API_KEY)

# Test health
curl $RAILWAY_URL/health

# Test API
curl -X POST $RAILWAY_URL/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"question": "Hello from Railway!"}'
```

**Expected response:**
```json
{
  "question": "Hello from Railway!",
  "answer": "Đây là câu trả lời từ AI agent (mock)...",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T10:30:00Z"
}
```

---

### Bước 9: View Logs

```bash
railway logs
```

**Hoặc:**
- Railway Dashboard → Project → Deployments → Logs

---

### Bước 10: Custom Domain (Optional)

```bash
railway domain add yourdomain.com
```

Sau đó add CNAME record trong DNS:
```
CNAME yourdomain.com → ai-agent-production-xxx.up.railway.app
```

---

## Deploy Render

### Tại Sao Chọn Render?

✅ **Ưu điểm:**
- Free tier 750 giờ/tháng
- Deploy từ GitHub (GitOps)
- Auto-deploy khi push code
- Managed Redis miễn phí
- Region gần Việt Nam hơn (Singapore)

❌ **Nhược điểm:**
- Setup phức tạp hơn Railway
- Free tier có cold start (spin down sau 15 phút idle)

---

### Bước 1: Push Code lên GitHub

```bash
# Initialize git (nếu chưa có)
git init

# Add files
git add .

# Commit
git commit -m "Production-ready AI agent for AICB-P1"

# Create repo trên GitHub
# https://github.com/new

# Add remote
git remote add origin https://github.com/yourusername/ai-agent-production.git

# Push
git push -u origin main
```

---

### Bước 2: Create Render Account

1. Vào [render.com](https://render.com)
2. Sign up với GitHub
3. Authorize Render to access repositories

---

### Bước 3: Create Blueprint

1. Dashboard → **"New +"** → **"Blueprint"**
2. Connect GitHub repository
3. Select `ai-agent-production` repo
4. Render tự động detect `render.yaml`

---

### Bước 4: Review Configuration

Render sẽ đọc `render.yaml`:

```yaml
services:
  - type: web
    name: ai-agent
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: AGENT_API_KEY
        generateValue: true  # Auto-generate
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
      - key: REDIS_URL
        fromService:
          name: redis
          property: connectionString

  - type: redis
    name: redis
    plan: free
    maxmemoryPolicy: allkeys-lru
```

---

### Bước 5: Set Environment Variables

Trong Render Dashboard:

1. Click vào service `ai-agent`
2. **Environment** tab
3. Add variables:

```
AGENT_API_KEY: <generate-strong-key>
OPENAI_API_KEY: sk-... (optional)
RATE_LIMIT_PER_MINUTE: 5
DAILY_BUDGET_USD: 5.0
```

**Generate strong key:**
```bash
openssl rand -hex 32
```

---

### Bước 6: Deploy

Click **"Apply"**

Render sẽ:
1. ✅ Provision Redis instance
2. ✅ Build Docker image
3. ✅ Deploy agent service
4. ✅ Assign public URL

**Wait 3-5 phút...**

---

### Bước 7: Get Public URL

Dashboard → Service → **URL**

Example: `https://ai-agent-production.onrender.com`

---

### Bước 8: Test Production

```bash
# Set variables
RENDER_URL="https://ai-agent-production.onrender.com"
API_KEY="<your-api-key-from-dashboard>"

# Test health
curl $RENDER_URL/health

# Test API
curl -X POST $RENDER_URL/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"question": "Hello from Render!"}'
```

---

### Bước 9: Enable Auto-Deploy

Dashboard → Service → Settings → **Build & Deploy**

Enable: **"Auto-Deploy: Yes"**

Bây giờ mỗi khi push code lên GitHub → Render tự động deploy!

```bash
# Make changes
echo "# Update" >> README.md
git add .
git commit -m "Update README"
git push

# Render sẽ tự động deploy!
```

---

### Bước 10: View Logs

Dashboard → Service → **Logs** tab

Hoặc dùng CLI:
```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# View logs
render logs ai-agent
```

---

## Deploy Google Cloud Run (Nâng Cao)

### Tại Sao Chọn Cloud Run?

✅ **Ưu điểm:**
- Scale to zero (chỉ trả tiền khi có traffic)
- 2 triệu requests/tháng miễn phí
- Latency thấp (nhiều regions)
- Enterprise-grade

❌ **Nhược điểm:**
- Phức tạp hơn
- Cần credit card
- Cần hiểu GCP

---

### Bước 1: Setup GCP

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

---

### Bước 2: Enable APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  redis.googleapis.com
```

---

### Bước 3: Create Redis Instance

```bash
gcloud redis instances create ai-agent-redis \
  --size=1 \
  --region=asia-southeast1 \
  --tier=basic
```

---

### Bước 4: Build & Push Image

```bash
# Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-agent

# Hoặc dùng cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml
```

---

### Bước 5: Deploy to Cloud Run

```bash
gcloud run deploy ai-agent \
  --image gcr.io/YOUR_PROJECT_ID/ai-agent \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_API_KEY=xxx,REDIS_URL=xxx
```

---

### Bước 6: Get URL

```bash
gcloud run services describe ai-agent \
  --region asia-southeast1 \
  --format 'value(status.url)'
```

---

## So Sánh Platforms

| Feature | Railway | Render | Cloud Run |
|---------|---------|--------|-----------|
| **Độ khó** | ⭐ Dễ nhất | ⭐⭐ Trung bình | ⭐⭐⭐ Khó |
| **Free tier** | $5 credit | 750h/tháng | 2M requests/tháng |
| **Cold start** | Không | Có (15 phút) | Có (configurable) |
| **Redis** | Included | Included | Separate service |
| **Auto-deploy** | CLI | GitHub | Cloud Build |
| **Custom domain** | Miễn phí | Miễn phí | Miễn phí |
| **Logs** | Real-time | Real-time | Cloud Logging |
| **Monitoring** | Basic | Basic | Advanced (Stackdriver) |
| **Best for** | Prototypes | Side projects | Production apps |

---

## Troubleshooting

### Issue 1: Railway Build Failed

**Error:**
```
Error: Cannot find module 'fastapi'
```

**Fix:**
```bash
# Check requirements.txt exists
ls requirements.txt

# Verify Dockerfile COPY requirements.txt
cat Dockerfile | grep requirements.txt
```

---

### Issue 2: Render Cold Start

**Problem:** First request sau 15 phút idle rất chậm (30s+)

**Fix:**
1. Upgrade to paid plan ($7/month) → No cold start
2. Hoặc dùng cron job để ping mỗi 10 phút:

```bash
# Crontab
*/10 * * * * curl https://your-app.onrender.com/health
```

---

### Issue 3: Redis Connection Failed

**Error:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Fix Railway:**
```bash
# Check Redis service
railway status

# Verify REDIS_URL
railway variables | grep REDIS_URL
```

**Fix Render:**
```bash
# Dashboard → Redis service → Check status
# Verify connection string in agent environment
```

---

### Issue 4: 401 Unauthorized in Production

**Problem:** API key không work

**Fix:**
```bash
# Railway
railway variables get AGENT_API_KEY

# Render
# Dashboard → Environment → Check AGENT_API_KEY

# Test với đúng key
curl -H "X-API-Key: <correct-key>" ...
```

---

### Issue 5: Rate Limit Quá Nhanh

**Problem:** Bị 429 sau 5 requests

**Fix:**
```bash
# Tăng limit
railway variables set RATE_LIMIT_PER_MINUTE=20

# Hoặc trong Render Dashboard
RATE_LIMIT_PER_MINUTE=20
```

---

## 📊 Monitoring Production

### Railway

```bash
# View logs
railway logs --tail

# View metrics
railway status
```

### Render

Dashboard → Service → **Metrics** tab:
- CPU usage
- Memory usage
- Request count
- Response time

### Cloud Run

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision"

# View metrics
gcloud monitoring dashboards list
```

---

## 🎯 Best Practices

### 1. Environment Variables

```bash
# ❌ KHÔNG hardcode
AGENT_API_KEY=123456

# ✅ Generate strong key
openssl rand -hex 32
```

### 2. Secrets Management

```bash
# Railway
railway variables set SECRET_KEY=xxx

# Render
# Dashboard → Environment → Add Secret

# Cloud Run
gcloud secrets create api-key --data-file=-
```

### 3. Health Checks

Đảm bảo `/health` và `/ready` hoạt động:

```bash
curl https://your-app.com/health
# Should return 200 OK
```

### 4. Logging

Dùng structured JSON logging:

```python
logger.info(json.dumps({
    "event": "request",
    "method": "POST",
    "path": "/ask",
    "status": 200,
    "duration_ms": 123
}))
```

### 5. Cost Monitoring

```bash
# Railway
railway usage

# Render
# Dashboard → Billing

# Cloud Run
gcloud billing accounts list
```

---

## ✅ Deployment Checklist

Trước khi submit assignment:

- [ ] Deploy thành công lên ít nhất 1 platform
- [ ] Public URL hoạt động
- [ ] `/health` returns 200
- [ ] `/ready` returns 200
- [ ] `/ask` requires API key
- [ ] Rate limiting works (429 after 5 requests)
- [ ] Logs visible trong dashboard
- [ ] Environment variables đã set đúng
- [ ] README.md có hướng dẫn deploy
- [ ] `.env.example` có đầy đủ variables

---

## 🎓 Submission

Submit vào assignment:

1. **GitHub repository URL**
2. **Public URL** (Railway/Render/Cloud Run)
3. **API Key** (để instructor test)
4. **Screenshot** của:
   - Dashboard showing deployment
   - Logs showing requests
   - `/health` endpoint response

---

## 📚 Resources

- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Chúc bạn deploy thành công! 🚀**

*Questions? Hỏi instructor hoặc check Troubleshooting section.*
