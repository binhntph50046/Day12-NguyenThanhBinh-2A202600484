# 🚀 DEPLOY TRÊN RAILWAY - REPO HIỆN TẠI

## ✅ ĐÃ CHUẨN BỊ:

- ✅ Xóa `render.yaml` (gây conflict)
- ✅ Tạo `railway.toml` với cấu hình đúng
- ✅ Dockerfile path: `06-lab-complete/Dockerfile`
- ✅ Health check: `/health`

## 🚀 DEPLOY NGAY (3 PHÚT):

### 1. Push Code
```powershell
git add .
git commit -m "Switch to Railway deployment - remove render.yaml conflicts"
git push origin main
```

### 2. Deploy trên Railway

#### Cách 1: Railway CLI (Nhanh nhất)
```powershell
# Install Railway CLI (nếu chưa có)
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

#### Cách 2: Railway Dashboard
1. Vào: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Select: `Day12-NguyenThanhBinh-2A202600484`
4. Railway tự động detect `railway.toml`
5. Click **Deploy**

### 3. Cấu hình Environment Variables

Trong Railway Dashboard → Variables:
```bash
PORT=8000
ENVIRONMENT=production
DEBUG=false
APP_NAME=Production AI Agent
APP_VERSION=1.0.0
AGENT_API_KEY=<generate-strong-key>
RATE_LIMIT_PER_MINUTE=5
DAILY_BUDGET_USD=5.0
LLM_MODEL=gpt-4o-mini
ALLOWED_ORIGINS=*
```

### 4. Generate API Key
```powershell
# PowerShell - Generate strong API key
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

Copy key và paste vào Railway Variables → AGENT_API_KEY

### 5. Get Public URL

Railway sẽ tự động tạo URL dạng:
```
https://day12-nguyenthanhbinh-2a202600484-production.up.railway.app
```

## 🧪 TEST PRODUCTION:

### Test Health Check
```powershell
$url = "https://your-railway-url.up.railway.app"
curl "$url/health"
```

### Test API
```powershell
$key = "your-api-key"
curl -X POST "$url/ask" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $key" `
  -d '{"question": "Hello from Railway!"}'
```

## 📸 SCREENSHOTS:

1. **Railway Dashboard** - Service "Active"
2. **Logs** - Startup messages
3. **Health Check** - Browser response

## 📝 NỘP BÀI:

- **Platform:** Railway
- **GitHub:** https://github.com/binhntph50046/Day12-NguyenThanhBinh-2A202600484
- **Public URL:** https://your-railway-url.up.railway.app
- **Student:** Nguyễn Thanh Bình - 2A202600484

---

## 🎯 TẠI SAO RAILWAY TỐT HỚN:

1. ✅ **Đơn giản hơn** - Ít cấu hình phức tạp
2. ✅ **Tự động detect** - Dockerfile, port, health check
3. ✅ **Ít lỗi** - Không có path conflicts như Render
4. ✅ **Free tier** - Đủ cho lab assignment
5. ✅ **Fast deploy** - 1-2 phút thay vì 5 phút

## 🚀 BẮt ĐẦU:

**Bước 1:** Push code (30 giây)
**Bước 2:** Deploy Railway (2 phút)  
**Bước 3:** Test production (30 giây)
**Bước 4:** Screenshots + nộp bài (2 phút)

**Tổng thời gian: 5 phút**

**LẦN NÀY CHẮC CHẮN THÀNH CÔNG! 🎯**