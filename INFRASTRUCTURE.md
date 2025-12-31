# tinyrisks.art Server Infrastructure Documentation

## 📋 Overview

This document describes the complete server infrastructure and deployment workflow for tinyrisks.art.

## 🖥️ Server Details

### Server Information
- **Host**: anditherobot.com
- **OS**: Ubuntu 22.04.5 LTS
- **User**: ubuntu
- **Domain**: tinyrisks.art (with www.tinyrisks.art)

### SSH Access
```bash
ssh ubuntu@anditherobot.com -i ~/.ssh/id_rsa
```

## 📁 Directory Structure

```
/var/www/tinyrisks.art/
├── .git/                    # Git repository
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions deployment workflow
├── htdocs/                  # Web root (served by nginx)
│   ├── index.html
│   ├── gallery.html
│   ├── poseidon.html
│   ├── writing.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   ├── videos/
│   │   │   └── placeholders/
│   │   └── uploads/         # User-uploaded images (not in git)
│   └── writing/
├── app.py                   # Flask app (not currently used)
├── requirements.txt
└── DEPLOYMENT.md
```

### File Permissions

**Critical**: All files in `htdocs/` must be owned by `www-data:www-data` for nginx to serve them.

```bash
# Check permissions
ls -la /var/www/tinyrisks.art/htdocs/

# Fix if needed
sudo chown -R www-data:www-data /var/www/tinyrisks.art/htdocs/
```

## 🌐 Web Server Configuration

### Nginx Setup

The site uses **nginx as a reverse proxy** to the Flask application running on port 5000.

**Config File**: `/etc/nginx/sites-available/tinyrisks.art`
**Enabled**: `/etc/nginx/sites-enabled/tinyrisks.art` → symlink to sites-available
**Template**: See `nginx.conf` in repository

### Key Configuration Details

Nginx proxies requests to the Flask application except for `/static/` which is served directly for performance:

```nginx
location /static/ {
    alias /var/www/tinyrisks.art/htdocs/static/;
    expires 30d;
}

location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

See `nginx.conf` in the repository for the complete configuration.

### SSL Certificates

- **Provider**: Let's Encrypt
- **Location**: `/etc/letsencrypt/live/tinyrisks.art/`
- **Renewal**: Auto-renewal via certbot (should be configured)

Check certificate status:
```bash
sudo certbot certificates
```

### Nginx Commands

```bash
# Test configuration
sudo nginx -t

# Reload configuration (no downtime)
sudo systemctl reload nginx

# Restart nginx (brief downtime)
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/tinyrisks.art.error.log
```

## 🚀 Deployment Workflow

### Architecture

```
Local Machine → GitHub Repository → GitHub Actions → Server
```

1. Developer pushes code to `master` branch
2. GitHub Actions workflow triggers automatically
3. Workflow SSHs into server
4. Pulls latest code via `git pull`
5. Fixes file permissions
6. Reloads nginx
7. Verifies site is accessible

### GitHub Repository

**URL**: https://github.com/anditherobot/tinyrisks.art
**Branch**: master (default branch)

### GitHub Actions Workflow

**File**: `.github/workflows/deploy.yml`

**Trigger**: Push to `master` branch

**Steps**:
1. **Checkout code** - Gets the latest code
2. **Setup SSH** - Configures SSH key from secrets
3. **Deploy to server** - Runs deployment commands via SSH:
   ```bash
   cd /var/www/tinyrisks.art
   git pull origin master
   sudo chown -R www-data:www-data htdocs/
   sudo systemctl reload nginx
   ```
4. **Verify deployment** - Checks if site returns 200 OK

### GitHub Secrets

Required secrets (configured via `gh secret set`):

| Secret | Value | Description |
|--------|-------|-------------|
| `SSH_PRIVATE_KEY` | Contents of `~/.ssh/id_rsa` | Private key for SSH access |
| `SERVER_HOST` | `anditherobot.com` | Server hostname |
| `SERVER_USER` | `ubuntu` | SSH username |
| `REMOTE_PATH` | `/var/www/tinyrisks.art` | Deployment directory |

**View secrets**:
```bash
gh secret list
```

**Update a secret**:
```bash
gh secret set SECRET_NAME < file_with_value
```

## 🔄 Git Configuration on Server

The server repository is configured for automated pulls:

```bash
# Current setup
git config --local user.email "deploy@tinyrisks.art"
git config --local user.name "Deploy Bot"
git config --global --add safe.directory /var/www/tinyrisks.art
```

**Remote**:
```bash
origin  https://github.com/anditherobot/tinyrisks.art.git
```

### Manual Deployment

If you need to deploy manually:

```bash
ssh ubuntu@anditherobot.com
cd /var/www/tinyrisks.art
git pull origin master
sudo chown -R www-data:www-data htdocs/
sudo systemctl reload nginx
```

## 🔍 Monitoring & Troubleshooting

### Check Deployment Status

```bash
# View recent deployments
gh run list

# View latest deployment
gh run view

# View specific deployment
gh run view <run-id>

# View logs for failed deployment
gh run view <run-id> --log-failed
```

### Verify Server Status

```bash
# Check what's deployed
ssh ubuntu@anditherobot.com "cd /var/www/tinyrisks.art && git log -1 --oneline"

# Check git status
ssh ubuntu@anditherobot.com "cd /var/www/tinyrisks.art && git status"

# Check file permissions
ssh ubuntu@anditherobot.com "ls -la /var/www/tinyrisks.art/htdocs/ | head -10"

# Test site accessibility
curl -I https://tinyrisks.art
```

### Common Issues

#### 1. Site Returns 404

**Cause**: Wrong file permissions
**Fix**:
```bash
ssh ubuntu@anditherobot.com "sudo chown -R www-data:www-data /var/www/tinyrisks.art/htdocs/"
```

#### 2. Deployment Fails with "Permission Denied"

**Cause**: SSH key not configured or incorrect
**Fix**:
```bash
# Test SSH access
ssh -i ~/.ssh/id_rsa ubuntu@anditherobot.com

# If fails, update GitHub secret
gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_rsa
```

#### 3. Git Pull Fails with "Dubious Ownership"

**Cause**: Git security check
**Fix**:
```bash
ssh ubuntu@anditherobot.com
git config --global --add safe.directory /var/www/tinyrisks.art
```

#### 4. Changes Not Appearing on Site

**Checklist**:
1. Verify deployment succeeded: `gh run list`
2. Check server has latest code: `ssh ubuntu@anditherobot.com "cd /var/www/tinyrisks.art && git log -1"`
3. Clear browser cache (Ctrl+Shift+R)
4. Check nginx logs: `ssh ubuntu@anditherobot.com "sudo tail /var/log/nginx/tinyrisks.art.error.log"`

## 🔐 Security Notes

### Sudo Permissions

The `ubuntu` user has sudo access to:
- `systemctl reload nginx`
- `systemctl restart nginx`
- `chown` commands

This is required for deployment to work.

### SSH Key Security

- Private key (`~/.ssh/id_rsa`) stored in GitHub Secrets
- Never commit private keys to repository
- Key is only used during GitHub Actions execution
- Key is deleted after each workflow run

### File Access

- Web files owned by `www-data:www-data`
- Git repository files owned by `ubuntu:ubuntu`
- Repository root (`/var/www/tinyrisks.art`) allows both users access

## 📊 Site Architecture

### Current Setup: Flask Application with Nginx Reverse Proxy

The site runs a **Flask application** (`app.py`) that:
- Serves HTML pages dynamically (including authentication-protected routes)
- Handles API endpoints for community gallery and image uploads
- Manages user authentication with Flask-Login

Nginx acts as a reverse proxy, forwarding requests to Flask while serving static assets directly for performance.

### Flask Service

**Service File**: `/etc/systemd/system/tinyrisks.service` (see `tinyrisks.service` in repository)
**Service Name**: `tinyrisks`
**Port**: 5000 (localhost only)

**Manage the service**:
```bash
sudo systemctl start tinyrisks
sudo systemctl stop tinyrisks
sudo systemctl restart tinyrisks
sudo systemctl status tinyrisks

# View logs
tail -f /var/www/tinyrisks.art/logs/flask_stderr.log
tail -f /var/www/tinyrisks.art/logs/flask_stdout.log
```

### Installation

If setting up the Flask service for the first time, see `INSTALLATION.md` for complete setup instructions.

## 📝 Maintenance Tasks

### Regular Maintenance

- **SSL Certificate Renewal**: Auto-renewed by certbot (verify with `sudo certbot renew --dry-run`)
- **System Updates**: Check with `ssh ubuntu@anditherobot.com "sudo apt update && sudo apt list --upgradable"`
- **Disk Space**: Monitor `/var/www/tinyrisks.art/htdocs/static/uploads/` for user uploads

### Backup Strategy

Currently no automated backups configured. Consider backing up:
- `/var/www/tinyrisks.art/htdocs/static/uploads/` (user-uploaded images)
- Nginx configuration files
- SSL certificates

**Quick backup of uploads**:
```bash
ssh ubuntu@anditherobot.com "tar -czf /tmp/uploads-backup.tar.gz /var/www/tinyrisks.art/htdocs/static/uploads/"
scp ubuntu@anditherobot.com:/tmp/uploads-backup.tar.gz ./uploads-backup-$(date +%Y%m%d).tar.gz
```

## 🎯 Quick Reference

### Deploy New Changes
```bash
git add .
git commit -m "Your message"
git push origin master
# GitHub Actions handles the rest!
```

### Check if Deployment Worked
```bash
gh run list --limit 1
```

### Manual Server Check
```bash
ssh ubuntu@anditherobot.com "cd /var/www/tinyrisks.art && git status && git log -1"
```

### View Live Site
```bash
curl -I https://tinyrisks.art
# Or visit: https://tinyrisks.art
```

## 📞 Support & Resources

- **GitHub Repository**: https://github.com/anditherobot/tinyrisks.art
- **GitHub Actions**: https://github.com/anditherobot/tinyrisks.art/actions
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

**Last Updated**: 2025-12-30
**Maintained by**: GitHub: @anditherobot
