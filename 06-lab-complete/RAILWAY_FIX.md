# 🔧 Fix Railway Deployment Error

> **Error:** "Error creating build plan with Railpack"

---

## 🎯 Nguyên Nhân

Railway không tìm thấy Dockerfile hoặc không hiểu cấu trúc project.

---

## ✅ Giải Pháp 1: Restructure Repository (Khuyến nghị)

### **Bước 1: Tạo Repository Mới Với Cấu Trúc Đúng**

```bash
# Tạo folder mới
cd "D:\AI thực chiến"
mkdir Lab12-Deploy
cd Lab12-Deploy

# Copy files từ 06-lab-complete
# Copy TẤT CẢ files từ 06-lab-complete vào Lab12-Deploy
# KHÔNG copy folder 06-lab-complete, chỉ copy NỘI DUNG bên trong
```

**Cấu trúc đúng:**
```
Lab12-Deploy/                    ← Root của Git repo
├── app/
│   ├── main.py
│   └── config.py
├── utils/
│   └── mock_llm.py
├── tests/
│   └── ...
├── Dockerfile                   ← Phải ở root!
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── railway.toml
└── README.md
```

### **Bước 2: Initialize Git**

```bash
cd Lab12-Deploy

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Production-ready AI agent for Railway"
```

### **Bước 3: Push to GitHub**

```bash
# Tạo repo mới trên GitHub
# https://github.com/new
# Tên: Lab12-NguyenThanhBinh-Deploy

# Add remote
git remote add origin https://github.com/yourusername/Lab12-NguyenThanhBinh-Deploy.git

# Push
git branch -M main
git push -u origin main
```

### **Bước 4: Deploy Lại Trên Railway**

1. **Xóa project cũ trên Railway:**
   - Vào Railway Dashboard
   - Click vào project "Day12-NguyenThanhBinh..."
   - Settings → Delete Project

2. **Tạo project mới:**
   - Railway Dashboard → New Project
   - Deploy from GitHub repo
   - Select: `Lab12-NguyenThanhBinh-Deploy`
   - Railway sẽ tự động detect Dockerfile và build

---

## ✅ Giải Pháp 2: Dùng Render (Dễ Hơn)

Nếu Railway vẫn gặp vấn đề, **dùng Render** (khuyến nghị cho beginners):

### **Bước 1: Chuẩn Bị Repository**

```bash
# Trong folder 06-lab-complete
git init
git add .
git commit -m "Production AI agent"

# Push to GitHub
git remote add origin https://github.com/yourusername/lab12-render.git
git push -u origin main
```

### **Bước 2: Deploy Trên Render**

1. **Vào:** https://render.com
2. **Sign up** với GitHub
3. **New → Blueprint**
4. **Connect repository**
5. **Render tự động đọc `render.yaml`**
6. **Click "Apply"**

### **Bước 3: Render Sẽ Tự Động:**
- ✅ Build Docker image
- ✅ Provision Redis
- ✅ Deploy service
- ✅ Assign public URL

### **Bước 4: Set Environment Variables**

**Trong Render Dashboard → Environment:**

```bash
AGENT_API_KEY=<generate-strong-key>
ENVIRONMENT=production
DEBUG=false
PORT=8000
```

**Generate API key:**
```powershell
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## ✅ Giải Pháp 3: Fix Railway Config

Nếu bạn muốn tiếp tục dùng Railway với cấu trúc hiện tại:

### **Bước 1: Tạo File `nixpacks.toml`**

Tạo file `nixpacks.toml` trong folder `06-lab-complete`:

```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### **Bước 2: Update Railway Settings**

1. **Trong Railway Dashboard:**
   - Settings → Build
   - Root Directory: `/06-lab-complete`
   - Dockerfile Path: `Dockerfile`

2. **Hoặc dùng Railway CLI:**
```bash
railway link
railway up --service 06-lab-complete
```

---

## 🎯 Khuyến Nghị: Dùng Render

**Lý do:**
- ✅ Dễ hơn Railway
- ✅ Tự động provision Redis
- ✅ Free tier 750h/month
- ✅ Ít lỗi hơn
- ✅ Documentation tốt hơn

**Steps:**
1. Push code to GitHub
2. Connect Render to GitHub
3. Deploy (1 click)
4. Done!

---

## 📝 Checklist

**Nếu dùng Railway:**
- [ ] Restructure repository (Dockerfile ở root)
- [ ] Push to new GitHub repo
- [ ] Delete old Railway project
- [ ] Create new Railway project
- [ ] Deploy from GitHub

**Nếu dùng Render:**
- [ ] Push code to GitHub
- [ ] Sign up Render
- [ ] New → Blueprint
- [ ] Connect repo
- [ ] Set environment variables
- [ ] Deploy

---

## 🆘 Vẫn Gặp Lỗi?

**Liên hệ:**
- Instructor: instructor@vinuni.edu.vn
- Attach: Screenshots của errors
- Describe: Các bước bạn đã làm

**Hoặc:**
- Dùng Render thay vì Railway
- Deploy local + ngrok (temporary solution)

---

## 📞 Cần Hỗ Trợ Ngay?

Cho tôi biết:
1. Bạn muốn dùng Railway hay Render?
2. Bạn có thể restructure repository không?
3. Screenshots của errors hiện tại

**Tôi sẽ hướng dẫn chi tiết từng bước!** 🚀
