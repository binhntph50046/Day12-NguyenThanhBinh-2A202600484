# Quick Deployment Check
$url = "https://nguyen-thanh-binh-agent.onrender.com"

Write-Host "🔍 Checking deployment status..." -ForegroundColor Yellow
Write-Host "URL: $url" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "Testing health endpoint..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "$url/health" -Method GET -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
        
        $json = $response.Content | ConvertFrom-Json
        Write-Host ""
        Write-Host "📊 Service Info:" -ForegroundColor Cyan
        Write-Host "   Status: $($json.status)"
        Write-Host "   Version: $($json.version)"
        Write-Host "   Environment: $($json.environment)"
        Write-Host "   Uptime: $($json.uptime_seconds) seconds"
        
        Write-Host ""
        Write-Host "🎯 NEXT STEPS:" -ForegroundColor Green
        Write-Host "1. Get API key from Render Dashboard → Environment → AGENT_API_KEY"
        Write-Host "2. Test API: .\test-production.ps1 -apiKey 'YOUR_KEY'"
        Write-Host "3. Take screenshots"
        Write-Host "4. Fill DEPLOYMENT_INFO.md"
        Write-Host "5. Submit to LMS"
        
    } else {
        Write-Host "❌ Unexpected status code: $($response.StatusCode)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ DEPLOYMENT NOT READY YET" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 This is normal if deployment just started." -ForegroundColor Yellow
    Write-Host "   Wait 2-3 minutes and run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Command: .\check-deployment.ps1" -ForegroundColor Gray
}