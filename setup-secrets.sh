#!/bin/bash
# Run this locally to set up GitHub secrets for deployment

echo "🔐 Setting up GitHub Secrets for deployment..."
echo ""

# Set the secrets using gh CLI
echo "Setting SERVER_HOST..."
gh secret set SERVER_HOST --body "anditherobot.com"

echo "Setting SERVER_USER..."
gh secret set SERVER_USER --body "ubuntu"

echo "Setting REMOTE_PATH..."
gh secret set REMOTE_PATH --body "/var/www/tinyrisks.art"

echo ""
echo "⚠️  You need to manually set SSH_PRIVATE_KEY:"
echo ""
echo "1. Get your SSH private key (the one that can access ubuntu@anditherobot.com)"
echo "2. Run this command:"
echo ""
echo "   gh secret set SSH_PRIVATE_KEY < /path/to/your/private/key"
echo ""
echo "   For example:"
echo "   gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_rsa"
echo ""
echo "After setting SSH_PRIVATE_KEY, your deployment will be ready!"
