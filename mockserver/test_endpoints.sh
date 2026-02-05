#!/bin/bash
# Test script for Mock Server Endpoints
SERVER_URL="http://localhost:5000"

echo "Testing Notifications..."
curl -X POST -H "Content-Type: application/json" -d '{"title":"Test","body":"Hello from Curl"}' $SERVER_URL/api/notifications
echo -e "\n"

echo "Testing File Listing (~)..."
curl "$SERVER_URL/api/files" | head -c 200
echo -e "\n..."

echo "Testing Clipboard (Read)..."
curl "$SERVER_URL/api/clipboard"
echo -e "\n"

echo "Testing Battery..."
curl "$SERVER_URL/api/battery"
echo -e "\n"

echo "Testing Media Status..."
curl "$SERVER_URL/api/media"
echo -e "\n"

echo "Done. To test Listeners, open $SERVER_URL/api/notifications/stream in a browser."
