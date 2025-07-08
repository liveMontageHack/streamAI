#!/bin/bash
# StreamAI Flask + React Development Startup Script

echo -e "\e[32mStarting StreamAI Flask Backend and React Frontend...\e[0m"

# Start Flask Backend from obs directory
echo -e "\e[33mStarting Flask API Server from obs directory...\e[0m"
(
  cd obs && python api_server.py &
)

# Wait a moment
sleep 2

# Start React Frontend
echo -e "\e[33mStarting React Frontend...\e[0m"
(
  cd frontend && npm run dev &
)

wait # Wait for background jobs if you want to keep the script running

echo
echo -e "\e[32mBoth servers are starting!\e[0m"
echo -e "\e[36mBackend API: http://localhost:5001\e[0m"
echo -e "\e[36mFrontend: http://localhost:5173\e[0m"
echo
read -n 1 -s -r -p "Press any key to continue..."
echo
