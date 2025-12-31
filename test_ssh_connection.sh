#!/bin/bash
# Test SSH Connection to Deployment Server
# This script verifies that SSH connectivity to the deployment server is working

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server configuration (from INFRASTRUCTURE.md)
SERVER_HOST="${SERVER_HOST:-anditherobot.com}"
SERVER_USER="${SERVER_USER:-ubuntu}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"

echo "=========================================="
echo "SSH Server Connection Test"
echo "=========================================="
echo ""
echo "Server: $SERVER_USER@$SERVER_HOST"
echo "SSH Key: $SSH_KEY"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ ERROR: SSH key not found at $SSH_KEY${NC}"
    echo "Please set SSH_KEY environment variable or ensure key exists at default location"
    exit 1
fi

echo -e "${YELLOW}→ Checking SSH key permissions...${NC}"
# Check permissions - works on both GNU and BSD systems
if [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "FreeBSD" ]; then
    # BSD/macOS
    KEY_PERMS=$(stat -f %Lp "$SSH_KEY" 2>/dev/null)
else
    # GNU/Linux
    KEY_PERMS=$(stat -c %a "$SSH_KEY" 2>/dev/null)
fi

if [ -n "$KEY_PERMS" ] && [ "$KEY_PERMS" != "600" ]; then
    echo -e "${YELLOW}⚠️  WARNING: SSH key has incorrect permissions ($KEY_PERMS). Should be 600.${NC}"
    echo "You may need to run: chmod 600 $SSH_KEY"
fi

echo -e "${YELLOW}→ Testing SSH connection...${NC}"

# Test SSH connection with timeout
if timeout 10 ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_HOST" "echo 'Connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful!${NC}"
    echo ""
    
    # Get server information if connection is successful
    echo -e "${YELLOW}→ Retrieving server information...${NC}"
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
echo "Operating System:"
lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME
echo ""
echo "Hostname:"
hostname
echo ""
echo "Uptime:"
uptime
echo ""
echo "Deployment directory status:"
if [ -d /var/www/tinyrisks.art ]; then
    echo "✅ /var/www/tinyrisks.art exists"
    cd /var/www/tinyrisks.art
    if [ -d .git ]; then
        echo "✅ Git repository initialized"
        echo "Current branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'N/A')"
        echo "Latest commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
    else
        echo "⚠️  Git repository not initialized"
    fi
else
    echo "⚠️  /var/www/tinyrisks.art does not exist"
fi
EOF
    
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ All SSH connectivity tests passed!"
    echo "==========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ SSH connection failed!${NC}"
    echo ""
    echo "Possible issues:"
    echo "  1. SSH key is not authorized on the server"
    echo "  2. Server is unreachable"
    echo "  3. Incorrect server hostname or username"
    echo "  4. Firewall blocking connection"
    echo ""
    echo "To authorize your SSH key, run:"
    echo "  ssh-copy-id -i $SSH_KEY $SERVER_USER@$SERVER_HOST"
    echo ""
    exit 1
fi
