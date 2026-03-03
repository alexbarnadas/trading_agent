# Startup script for Trading Bot VM
# Run this in PowerShell to start both Backend and Frontend

Write-Host "Starting Trading Bot Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command .\venv\Scripts\uvicorn api.main:app --host 0.0.0.0 --port 8000"

Write-Host "Starting Trading Bot Frontend..." -ForegroundColor Green
Set-Location frontend
npm run dev
