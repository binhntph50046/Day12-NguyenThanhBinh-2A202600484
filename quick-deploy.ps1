# ============================================================
# Quick Deploy Script - Deploy Dự Án Hiện Tại
# 
# Usage: .\quick-deploy.ps1
# ============================================================

Write-Host "================================" -ForegroundColor Blue
Write-Host "  QUICK DEPLOY TO RENDER" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Get current directory
$currentDir = Get-Location

Write-Host "[1/5] Checking Git..." -ForegroundColor Cyan

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git not installed!" -ForegroundColor Red
    Write-Host "Download: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if git repo exists
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "OK: Git initialized" -ForegroundColor Green
} else {
    Write-Host "OK: Git repository exists" -ForegroundColor Green
}
Write-Host ""

# Add and commit
Write-Host "[2/5] Committing changes..." -ForegroundColor Cyan
git add .
git commit -m "Production AI Agent - Lab Day 12" 2>$null
Write-Host "OK: Changes committed" -ForegroundColor Green
Write-Host ""

# Check remote
Write-Host "[3/5] Checking GitHub remote..." -ForegroundColor Cyan
$remote = git remote get-url origin 2>$null

if ($remote) {
    Write-Host "OK: Remote exists: $remote" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "[4/5] Pushing to GitHub..." -ForegroundColor Cyan
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Pushed to GitHub" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Push failed. You may need to set up authentication." -ForegroundColor Yellow
        Write-Host "Create Personal Access Token: https://github.com/settings/tokens" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: No remote configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Create GitHub repository:" -ForegroundColor Yellow
    Write-Host "   https://github.com/new" -ForegroundColor White
    Write-Host "   Name: Day12-NguyenThanhBinh-2A202600484" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Add remote and push:" -ForegroundColor Yellow
    Write-Host "   git remote add origin https://github.com/yourusername/Day12-NguyenThanhBinh-2A202600484.git" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor White
    Write-Host ""
}

# Generate API key
Write-Host ""
Write-Host "[5/5] Generating API key..." -ForegroundColor Cyan
$apiKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Your API Key: " -NoNewline -ForegroundColor Green
Write-Host "$apiKey" -ForegroundColor Yellow
Write-Host ""
Write-Host "SAVE THIS KEY! You'll need it for Render deployment." -ForegroundColor Red
Write-Host ""

# Next steps
Write-Host "================================" -ForegroundColor Blue
Write-Host "  NEXT STEPS" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

Write-Host "1. Deploy on Render:" -ForegroundColor Cyan
Write-Host "   - Go to: https://render.com" -ForegroundColor White
Write-Host "   - Sign up with GitHub" -ForegroundColor White
Write-Host "   - New -> Blueprint" -ForegroundColor White
Write-Host "   - Connect repository: Day12-NguyenThanhBinh-2A202600484" -ForegroundColor White
Write-Host "   - Click 'Apply'" -ForegroundColor White
Write-Host ""

Write-Host "2. Set Environment Variables in Render:" -ForegroundColor Cyan
Write-Host "   AGENT_API_KEY=$apiKey" -ForegroundColor White
Write-Host ""

Write-Host "3. Wait for deployment (~3-5 minutes)" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. Test your deployment:" -ForegroundColor Cyan
Write-Host "   curl https://your-service.onrender.com/health" -ForegroundColor White
Write-Host ""

Write-Host "5. Read full guide:" -ForegroundColor Cyan
Write-Host "   notepad DEPLOY_CURRENT_PROJECT.md" -ForegroundColor White
Write-Host ""

Write-Host "================================" -ForegroundColor Blue
Write-Host "  READY TO DEPLOY!" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Save API key to file
$apiKey | Out-File -FilePath "API_KEY.txt" -Encoding UTF8
Write-Host "API Key saved to: API_KEY.txt" -ForegroundColor Green
Write-Host ""
