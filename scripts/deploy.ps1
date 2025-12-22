# EdPear Vercel Deployment Script (PowerShell)
# This script helps you deploy the EdPear platform to Vercel and sync environment variables

# Ensure we are running from the root directory
if ($PSScriptRoot -and (Split-Path $PSScriptRoot -Leaf) -eq "scripts") {
    Set-Location (Split-Path $PSScriptRoot -Parent)
    Write-Host "[Info] Switched to project root directory: $(Get-Location)" -ForegroundColor Gray
}

Write-Host "[EdPear] Vercel Deployment" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "[Info] Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Login if needed
Write-Host "[Auth] Checking Vercel login status..." -ForegroundColor Gray
$vercelUser = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[Error] Not logged in to Vercel. Please login:" -ForegroundColor Yellow
    vercel login
} else {
    Write-Host "[Success] Logged in as: $vercelUser" -ForegroundColor Green
}

Write-Host ""
Write-Host "Choose deployment type:"
Write-Host "1) Preview (Development)"
Write-Host "2) Production (Live)"
Write-Host "3) Sync Environment Variables from .env.local"
$choice = Read-Host "Enter choice [1-3]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "[Deploy] Deploying to Preview..." -ForegroundColor Yellow
        vercel
    }
    "2" {
        Write-Host ""
        Write-Host "[Deploy] Deploying to Production..." -ForegroundColor Yellow
        vercel --prod
    }
    "3" {
        Write-Host ""
        Write-Host "[Sync] Syncing environment variables..." -ForegroundColor Yellow
        if (Test-Path ".env.local") {
            Write-Host "[Tip] To sync variables, it's recommended to:" -ForegroundColor Cyan
            Write-Host "   1. Go to https://vercel.com/dashboard" -ForegroundColor Gray
            Write-Host "   2. Project Settings > Environment Variables" -ForegroundColor Gray
            Write-Host "   3. Paste the contents of your .env.local file" -ForegroundColor Gray
            Write-Host ""
            Write-Host "This script will try to push .env.local to Vercel automatically." -ForegroundColor Gray
            
            $confirm = Read-Host "Push .env.local to Vercel now? (y/n)"
            if ($confirm -eq "y") {
                Write-Host "[Sync] Pushing .env.local..." -ForegroundColor Yellow
                # Check if .env.local exists, if so temporarily copy to .env for vercel push
                # vercel env push .env.local is actually correct for some versions but let's be safe
                vercel env push .env.local
            }
        } else {
            Write-Host "[Error] .env.local not found. Please create it first." -ForegroundColor Red
        }
    }
    default {
        Write-Host "[Error] Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Process complete!" -ForegroundColor Green
