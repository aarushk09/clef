# EdPear Publishing Script (PowerShell)
# This script helps you publish both CLI and SDK packages to npm

Write-Host "🚀 EdPear Publishing Script" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in to npm
try {
    $npmUser = npm whoami 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in"
    }
    Write-Host "✅ Logged in as: $npmUser" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to npm" -ForegroundColor Red
    Write-Host "Please run: npm login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Publishing the combined SDK and CLI (@edpear/sdk)..." -ForegroundColor Yellow

Set-Location edpear-sdk
npm run build
if ($LASTEXITCODE -eq 0) {
    npm publish --access public
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SDK and CLI published successfully!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 Publishing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify at:"
Write-Host "  SDK: https://www.npmjs.com/package/@edpear/sdk"
