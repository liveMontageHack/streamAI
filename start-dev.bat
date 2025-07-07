@echo off
echo Starting StreamAI Flask Backend and React Frontend...
echo.

echo Starting Flask API Server from obs directory...
cd obs
start "StreamAI Flask Backend" cmd /k "python api_server.py"

echo.
echo Starting React Frontend...
cd ..\frontend
start "StreamAI React Frontend" cmd /k "npm run dev"

echo.
echo Both servers are starting!
echo Backend API: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul
