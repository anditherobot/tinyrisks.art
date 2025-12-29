# Deployment Guide for tinyrisks.art

This project uses GitHub Actions for automatic deployment to your server.

## 🎯 Overview

When you push to the `main` branch, GitHub Actions will automatically:
1. SSH into your server
2. Pull the latest code
3. Restart the Flask service
4. Verify the site is live

## 📋 One-Time Setup

### Step 1: Set up SSH Key (if needed)

You need an SSH private key that can access `ubuntu@anditherobot.com`.

If you don't have one yet:
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-deploy@tinyrisks.art"

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/id_ed25519 ubuntu@anditherobot.com

# Test the connection
ssh -i ~/.ssh/id_ed25519 ubuntu@anditherobot.com
```

### Step 2: Set GitHub Secrets

The basic secrets have been set. Now add your SSH private key:

```bash
# From your local machine, run:
gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_ed25519

# Or if using a different key:
gh secret set SSH_PRIVATE_KEY < /path/to/your/private/key
```

Verify all secrets are set:
```bash
gh secret list
```

You should see:
- `REMOTE_PATH`
- `SERVER_HOST`
- `SERVER_USER`
- `SSH_PRIVATE_KEY`

### Step 3: Set up Git on the Server

SSH into your server and run the setup script:

```bash
# SSH into your server
ssh ubuntu@anditherobot.com

# Download and run the setup script
curl -O https://raw.githubusercontent.com/anditherobot/tinyrisks.art/master/server-setup.sh
chmod +x server-setup.sh
sudo ./server-setup.sh
```

Or manually:
```bash
ssh ubuntu@anditherobot.com
cd /var/www/tinyrisks.art
git init
git remote add origin https://github.com/anditherobot/tinyrisks.art.git
git config --local user.email "deploy@tinyrisks.art"
git config --local user.name "Deploy Bot"
git fetch origin master
git checkout -B master origin/master
```

### Step 4: Test Deployment

Push a change to trigger deployment:

```bash
# Make a small change
echo "# Test" >> README.md
git add README.md
git commit -m "Test deployment"
git push origin master
```

Watch the deployment:
```bash
# View the GitHub Actions run
gh run watch
```

## 🚀 Daily Usage

After setup, deployment is automatic:

```bash
git add .
git commit -m "Your commit message"
git push origin master
```

GitHub Actions will handle the rest!

## 🔍 Troubleshooting

### Check deployment status
```bash
gh run list
gh run view  # View latest run
```

### View server logs
```bash
ssh ubuntu@anditherobot.com 'tail -n 50 /var/www/tinyrisks.art/logs/flask_stderr.log'
```

### Manual deployment
```bash
ssh ubuntu@anditherobot.com
cd /var/www/tinyrisks.art
git pull origin master
sudo systemctl restart tinyrisks
sudo systemctl status tinyrisks
```

## 📁 Repository

https://github.com/anditherobot/tinyrisks.art

## ⚙️ Configuration

Edit deployment settings in `.github/workflows/deploy.yml`

Server configuration:
- **Host**: anditherobot.com
- **User**: ubuntu
- **Path**: /var/www/tinyrisks.art
- **Service**: tinyrisks
- **Domain**: tinyrisks.art

