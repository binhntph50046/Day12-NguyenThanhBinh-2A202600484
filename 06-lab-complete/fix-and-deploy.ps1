# ============================================================
# Script Tự Động Fix và Deploy
# 
# Usage: .\fix-and-deploy.ps1
# ============================================================

Write-Host "================================" -ForegroundColor Blue
Write-Host "  FIX & DEPLOY SCRIPT" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Kiểm tra Git
Write-Host "[1/6] Checking Git..." -ForegroundColor Cyan
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git not installed!" -ForegroundColor Red
    Write-Host "Download: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Git installed" -ForegroundColor Green
Write-Host ""

# Tạo folder mới
Write-Host "[2/6] Creating new folder structure..." -ForegroundColor Cyan
$parentDir = Split-Path -Parent $PSScriptRoot
$newDir = Join-Path $parentDir "Lab12-Deploy"

if (Test-Path $newDir) {
    Write-Host "WARNING: Folder already exists. Removing..." -ForegroundColor Yellow
    Remove-Item $newDir -Recurse -Force
}

New-Item -ItemType Directory -Path $newDir | Out-Null
Write-Host "OK: Created $newDir" -ForegroundColor Green
Write-Host ""

# Copy files
Write-Host "[3/6] Copying files..." -ForegroundColor Cyan

# Copy app folder
Copy-Item -Path (Join-Path $PSScriptRoot "app") -Destination $newDir -Recurse
Write-Host "  Copied: app/" -ForegroundColor Gray

# Copy utils folder
$utilsSource = Join-Path (Split-Path -Parent $PSScriptRoot) "utils"
if (Test-Path $utilsSource) {
    Copy-Item -Path $utilsSource -Destination $newDir -Recurse
    Write-Host "  Copied: utils/" -ForegroundColor Gray
}

# Copy tests folder
Copy-Item -Path (Join-Path $PSScriptRoot "tests") -Destination $newDir -Recurse
Write-Host "  Copied: tests/" -ForegroundColor Gray

# Copy root files
$rootFiles = @(
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    ".env.example",
    ".dockerignore",
    "railway.toml",
    "render.yaml",
    "README.md",
    "DEPLOYMENT_GUIDE.md",
    "QUICK_START.md"
)

foreach ($file in $rootFiles) {
    $sourcePath = Join-Path $PSScriptRoot $file
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $newDir
        Write-Host "  Copied: $file" -ForegroundColor Gray
    }
}

Write-Host "OK: All files copied" -ForegroundColor Green
Write-Host ""

# Initialize Git
Write-Host "[4/6] Initializing Git repository..." -ForegroundColor Cyan
Set-Location $newDir
git init | Out-Null
git add . | Out-Null
git commit -m "Production-ready AI agent" | Out-Null
Write-Host "OK: Git initialized and committed" -ForegroundColor Green
Write-Host ""

# Instructions
Write-Host "[5/6] Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create GitHub repository:" -ForegroundColor Yellow
Write-Host "   https://github.com/new" -ForegroundColor White
Write-Host "   Name: Lab12-NguyenThanhBinh-Deploy" -ForegroundColor White
Write-Host ""
Write-Host "2. Push to GitHub:" -ForegroundColor Yellow
Write-Host "   cd $newDir" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/yourusername/Lab12-NguyenThanhBinh-Deploy.git" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "3. Deploy on Render (Recommended):" -ForegroundColor Yellow
Write-Host "   - Go to: https://render.com" -ForegroundColor White
Write-Host "   - Sign up with GitHub" -ForegroundColor White
Write-Host "   - New -> Blueprint" -ForegroundColor White
Write-Host "   - Connect repository" -ForegroundColor White
Write-Host "   - Click 'Apply'" -ForegroundColor White
Write-Host ""

# Generate API key
Write-Host "[6/6] Generating API key..." -ForegroundColor Cyan
$apiKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Your API Key: $apiKey" -ForegroundColor Green
Write-Host ""
Write-Host "Save this key! You'll need it for deployment." -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Host "================================" -ForegroundColor Blue
Write-Host "  SETUP COMPLETE!" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""
Write-Host "New folder created at:" -ForegroundColor Green
Write-Host "$newDir" -ForegroundColor White
Write-Host ""
Write-Host "Next: Follow steps above to deploy" -ForegroundColor Cyan
Write-Host ""

# Open folder
Write-Host "Opening folder..." -ForegroundColor Cyan
Start-Process explorer.exe $newDir
