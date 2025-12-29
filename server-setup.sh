#!/bin/bash
# Run this script on your server to set up GitHub deployment

REMOTE_PATH="/var/www/tinyrisks.art"
REPO_URL="https://github.com/YOUR_USERNAME/tinyrisks.art.git"  # Will be updated

echo "🔧 Setting up GitHub deployment on server..."

# Navigate to the deployment directory
cd $REMOTE_PATH || exit 1

# Check if already a git repo
if [ -d ".git" ]; then
    echo "✓ Git repository already exists"
else
    echo "→ Initializing git repository..."
    git init
    git remote add origin $REPO_URL
fi

# Set git config for the directory
echo "→ Configuring git..."
git config --local user.email "deploy@tinyrisks.art"
git config --local user.name "Deploy Bot"

# Create htdocs directory if it doesn't exist
mkdir -p htdocs

echo "→ Fetching from GitHub..."
git fetch origin main

# Check if we have local changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠ Warning: Local changes detected. Stashing them..."
    git stash
fi

echo "→ Checking out main branch..."
git checkout -B main origin/main

echo ""
echo "✅ Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your SSH key is added to GitHub (for pulls)"
echo "2. Test manual pull: cd $REMOTE_PATH && git pull"
echo "3. Push from your local machine to trigger deployment"
