# Test Production Deployment
# Chạy script này sau khi Render deploy xong

param(
    [string]$url = "https://nguyen-thanh-binh-agent.onrender.com",
    [string]$apiKey = ""
)

Write-Host "🧪 TESTING PRODUCTION DEPLOYMENT" -ForegroundColor Green
Write-Host "URL: $url" -ForegroundColor Yellow
Write-Host ""

# Test 1: Health Check
Write-Host "1️⃣ Testing Health Check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$url/health" -Method GET
    Write-Host "✅ Health Check: PASS" -ForegroundColor Green
    Write-Host "   Status: $($health.status)"
    Write-Host "   Version: $($health.version)"
    Write-Host "   Environment: $($health.environment)"
    Write-Host "   Uptime: $($health.uptime_seconds)s"
} catch {
    Write-Host "❌ Health Check: FAIL" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)"
    return
}

Write-Host ""

# Test 2: API without key (should fail)
Write-Host "2️⃣ Testing API without key (should fail)..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$url/ask" -Method POST -ContentType "application/json" -Body '{"question": "test"}'
    Write-Host "❌ API No Key: FAIL (should have failed but didn't)" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ API No Key: PASS (correctly returned 401)" -ForegroundColor Green
    } else {
        Write-Host "❌ API No Key: FAIL (wrong error code: $($_.Exception.Response.StatusCode))" -ForegroundColor Red
    }
}

Write-Host ""

# Test 3: API with key (if provided)
if ($apiKey -ne "") {
    Write-Host "3️⃣ Testing API with key..." -ForegroundColor Cyan
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "X-API-Key" = $apiKey
        }
        $body = '{"question": "Hello from production test!"}'
        $response = Invoke-RestMethod -Uri "$url/ask" -Method POST -Headers $headers -Body $body
        
        Write-Host "✅ API With Key: PASS" -ForegroundColor Green
        Write-Host "   Question: $($response.question)"
        Write-Host "   Answer: $($response.answer.Substring(0, [Math]::Min(50, $response.answer.Length)))..."
        Write-Host "   Model: $($response.model)"
    } catch {
        Write-Host "❌ API With Key: FAIL" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)"
    }
} else {
    Write-Host "3️⃣ Skipping API test (no API key provided)" -ForegroundColor Yellow
    Write-Host "   To test with API key, run:" -ForegroundColor Gray
    Write-Host "   .\test-production.ps1 -apiKey 'YOUR_API_KEY'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Green
Write-Host "1. Get API key from Render Dashboard → Environment → AGENT_API_KEY"
Write-Host "2. Run: .\test-production.ps1 -apiKey 'YOUR_KEY'"
Write-Host "3. Take screenshots of Render dashboard"
Write-Host "4. Fill out DEPLOYMENT_INFO.md"
Write-Host "5. Submit to LMS"