# StreamAI Flask + React Development Startup Script
Write-Host "Starting StreamAI Flask Backend and React Frontend..." -ForegroundColor Green

# Start Flask Backend from obs directory
Write-Host "Starting Flask API Server from obs directory..." -ForegroundColor Yellow
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd obs; python api_server.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start React Frontend  
Write-Host "Starting React Frontend..." -ForegroundColor Yellow
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "Both servers are starting!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:5001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
