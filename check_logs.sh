#!/bin/bash

# Configuration
SERVER_USER="ubuntu"
SERVER_HOST="anditherobot.com"
APP_DIR="/var/www/tinyrisks.art"
REMOTE_LOG_PATH="/var/www/tinyrisks.art/logs/flask_stderr.log"

echo "🔍 Checking logs for TinyRisks.art..."
echo "----------------------------------------"

# Check if we want Nginx or Flask logs
if [ "$1" == "nginx" ]; then
    echo "📄 Fetching recent Nginx error logs..."
    ssh $SERVER_USER@$SERVER_HOST "sudo tail -n 50 /var/log/nginx/error.log"
elif [ "$1" == "access" ]; then
    echo "📄 Fetching recent Nginx access logs..."
    ssh $SERVER_USER@$SERVER_HOST "sudo tail -n 50 /var/log/nginx/access.log"
else
    echo "📄 Fetching recent Flask/Systemd logs..."
    # Try systemd journal first as it's the primary logging method in the service file
    ssh $SERVER_USER@$SERVER_HOST "sudo journalctl -u tinyrisks -n 50 --no-pager"
    
    # Also check if there are any file-based logs just in case
    echo ""
    echo "----------------------------------------"
    echo "📄 Checking for file-based logs..."
    ssh $SERVER_USER@$SERVER_HOST "if [ -f $REMOTE_LOG_PATH ]; then tail -n 20 $REMOTE_LOG_PATH; else echo 'No separate Flask log file found (normal if using journald)'; fi"
fi

echo "----------------------------------------"
echo "✅ Done."
