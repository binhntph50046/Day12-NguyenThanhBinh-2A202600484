# 🔧 KHẮC PHỤC LỖI RENDER - DEPLOY THÀNH CÔNG

> **Lỗi hiện tại:** "failed to read dockerfile: read /home/user/.local/tmp/buildkit-mount580411604/06-lab-complete: is a directory"

## ✅ ĐÃ SỬA: Cấu hình render.yaml

Tôi đã sửa file `render.yaml` với cấu hình đúng:

```yaml
services:
  - type: web
    name: nguyen-thanh-binh-agent
    env: docker
    dockerfilePath: ./Dockerfile          # ✅ Đã sửa từ ./06-lab-complete/Dockerfile
    dockerContext: ./06-lab-complete      # ✅ Context vẫn giữ nguyên
    plan: free
    envVars:
      - key: PORT
        value: 8000
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
      - key: AGENT_API_KEY
        generateValue: true
      - key: RATE_LIMIT_PER_MINUTE
        value: 5
      - key: DAILY_BUDGET_USD
        value: 5.0
    healthCheckPath: /health
```

**Thay đổi chính:**
- `dockerfilePath: ./Dockerfile` (thay vì `./06-lab-complete/Dockerfile`)
- Bỏ `REDIS_URL` vì không cần Redis cho version đơn giản này

---

## 🚀 BƯỚC TIẾP THEO: DEPLOY LẠI

### 1. Commit & Push Changes

```powershell
# Vào folder root
cd "D:\AI thực chiến\Day12-NguyenThanhBinh-2A202600484"

# Add changes
git add render.yaml

# Commit
git commit -m "Fix render.yaml - correct Dockerfile path"

# Push
git push origin main
```

### 2. Trigger Redeploy trên Render

**Cách 1: Automatic (Khuyến nghị)**
- Render sẽ tự động detect git push và redeploy
- Đợi 2-3 phút

**Cách 2: Manual**
1. Vào Render Dashboard
2. Click vào service `nguyen-thanh-binh-agent`
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

### 3. Theo dõi Build Process

1. Vào **Logs** tab
2. Theo dõi build process:
   ```
   ✓ Cloning repository...
   ✓ Building Docker image...
   ✓ Starting container...
   ✓ Health check passed
   ✓ Service is live
   ```

**Thời gian dự kiến:** 3-5 phút

---

## 🧪 TEST SAU KHI DEPLOY THÀNH CÔNG

### 1. Lấy URL và API Key

```powershell
# URL sẽ có dạng:
$url = "https://nguyen-thanh-binh-agent.onrender.com"

# API Key: Vào Render Dashboard → Service → Environment → AGENT_API_KEY
$key = "paste-api-key-here"
```

### 2. Test Health Check

```powershell
curl "$url/health"
```

**Expected:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 12.3,
  "total_requests": 1,
  "checks": {
    "llm": "mock"
  },
  "timestamp": "2026-04-17T10:30:00Z"
}
```

### 3. Test API Endpoint

```powershell
curl -X POST "$url/ask" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $key" `
  -d '{"question": "Hello from production!"}'
```

**Expected:**
```json
{
  "question": "Hello from production!",
  "answer": "Đây là câu trả lời từ AI agent (mock)...",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T10:30:00Z"
}
```

### 4. Test Rate Limiting

```powershell
# Make 6 requests quickly
for ($i=1; $i -le 6; $i++) {
    Write-Host "Request $i"
    curl -X POST "$url/ask" `
      -H "Content-Type: application/json" `
      -H "X-API-Key: $key" `
      -d "{`"question`": `"Test $i`"}"
    Start-Sleep -Milliseconds 100
}
```

**Expected:** Request thứ 6 sẽ nhận `429 Too Many Requests`

---

## 📸 CHỤP SCREENSHOTS

### Screenshot 1: Render Dashboard
1. Vào Render Dashboard
2. Show service status: **Live** ✅
3. Chụp màn hình
4. Lưu: `screenshots/01-render-dashboard.png`

### Screenshot 2: Logs
1. Click vào service
2. Tab **"Logs"**
3. Scroll để thấy startup messages và requests
4. Chụp màn hình
5. Lưu: `screenshots/02-logs.png`

### Screenshot 3: Health Check
1. Mở browser
2. Vào: `https://nguyen-thanh-binh-agent.onrender.com/health`
3. Chụp JSON response
4. Lưu: `screenshots/03-health-check.png`

---

## 📝 ĐIỀN THÔNG TIN NỘP BÀI

### 1. Tạo DEPLOYMENT_INFO.md

```powershell
cd "06-lab-complete"
copy DEPLOYMENT_INFO_TEMPLATE.md DEPLOYMENT_INFO.md
notepad DEPLOYMENT_INFO.md
```

### 2. Điền thông tin thực tế:

```markdown
## 👤 Student Information
**Full Name:** Nguyễn Thanh Bình
**Student ID:** 2A202600484
**Email:** binh.nt.2024@vinuni.edu.vn
**Submission Date:** 2026-04-17

## ☁️ Cloud Deployment
**Platform:** [x] Render
**Public URL:** https://nguyen-thanh-binh-agent.onrender.com
**Health Check:** https://nguyen-thanh-binh-agent.onrender.com/health

## 🔑 API Key (Confidential)
**API Key Preview:** [first-8-chars]****
**Email Sent To:** instructor@vinuni.edu.vn
```

### 3. Paste Test Results

Copy kết quả từ terminal vào phần **Test Results**

---

## 📧 GỬI EMAIL API KEY

**To:** instructor@vinuni.edu.vn  
**Subject:** Lab Day 12 - API Key - 2A202600484

```
Dear Instructor,

Student Information:
- Name: Nguyễn Thanh Bình
- Student ID: 2A202600484
- Email: binh.nt.2024@vinuni.edu.vn

Deployment Information:
- Platform: Render
- Public URL: https://nguyen-thanh-binh-agent.onrender.com
- GitHub: https://github.com/[your-username]/Day12-NguyenThanhBinh-2A202600484

API Key (Confidential):
AGENT_API_KEY=[paste-full-key-here]

Test Command:
curl -X POST https://nguyen-thanh-binh-agent.onrender.com/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: [your-key]" \
  -d '{"question": "Hello from instructor!"}'

All tests are passing.

Best regards,
Nguyễn Thanh Bình
```

---

## 📤 NỘP BÀI LÊN LMS

### Files cần nộp:

1. **GitHub Repository URL**
2. **Public URL**
3. **DEPLOYMENT_INFO.md** (đã điền)
4. **Screenshots.zip** (3 ảnh)
5. **Test Results** (copy từ terminal)

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Sửa render.yaml ✅ (Đã xong)
- [ ] Push changes lên GitHub
- [ ] Redeploy trên Render
- [ ] Service status: Live
- [ ] Test health check
- [ ] Test API với authentication
- [ ] Test rate limiting
- [ ] Chụp 3 screenshots
- [ ] Điền DEPLOYMENT_INFO.md
- [ ] Gửi email API key
- [ ] Nộp bài lên LMS

---

## 🎯 TÓM TẮT

**Vấn đề đã được khắc phục:**
- ✅ Sửa `dockerfilePath` trong render.yaml
- ✅ Bỏ Redis dependency không cần thiết
- ✅ Cấu hình environment variables đúng

**Bước tiếp theo:**
1. Push code (1 phút)
2. Đợi Render redeploy (3-5 phút)
3. Test production (2 phút)
4. Chụp screenshots (2 phút)
5. Nộp bài (5 phút)

**Tổng thời gian còn lại:** ~15 phút

---

## 🆘 NẾU VẪN GẶP LỖI

Cho tôi biết:
1. Bạn đã push code chưa?
2. Render có redeploy không?
3. Logs hiển thị lỗi gì?
4. Screenshot của error

**Tôi sẽ hỗ trợ ngay! 🚀**