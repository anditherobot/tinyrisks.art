# Fix for /admin 404 Error

## Problem

The `/admin` route was returning a 404 error because nginx was configured to serve static files directly from the `htdocs/` directory, but there is no file or directory named `/admin` - only `/admin.html`.

The Flask application in `app.py` has a route for `/admin` that requires authentication and serves `admin.html`, but nginx was never forwarding requests to the Flask application.

## Root Cause

The production server infrastructure was set up to serve static files directly via nginx, without running the Flask application. When users requested `/admin`, nginx looked for:
- `/var/www/tinyrisks.art/htdocs/admin` (directory) - not found
- `/var/www/tinyrisks.art/htdocs/admin` (file) - not found

Result: 404 error

## Solution

The Flask application needs to be running and nginx needs to be configured as a reverse proxy to forward requests to Flask. This allows:

1. **Dynamic routes** like `/admin`, `/login`, `/api/*` to be handled by Flask
2. **Authentication** to work properly (Flask-Login manages sessions)
3. **Static files** to still be served efficiently (nginx can serve `/static/` directly)

## Changes Made

### 1. Created nginx configuration (`nginx.conf`)
- Configured nginx to proxy all requests to Flask running on port 5000
- Static files under `/static/` are served directly by nginx for performance
- Includes SSL configuration and security headers

### 2. Created systemd service file (`tinyrisks.service`)
- Defines how to run the Flask application as a system service
- Runs as `www-data` user
- Logs to `/var/www/tinyrisks.art/logs/`
- Auto-restarts on failure

### 3. Created installation guide (`INSTALLATION.md`)
- Step-by-step instructions for setting up the Flask service
- Troubleshooting guide
- Security notes

### 4. Updated infrastructure documentation (`INFRASTRUCTURE.md`)
- Corrected architecture description
- Documented the Flask service setup
- Updated nginx configuration details

### 5. Updated deployment workflow (`.github/workflows/deploy.yml`)
- Added creation of `logs/` directory
- Added permission setting for logs directory
- Already includes `systemctl restart tinyrisks` (which confirms service should exist)

## Required Actions on Production Server

To fix the 404 error, the server administrator needs to perform these one-time setup steps:

### 1. Install the systemd service

```bash
ssh ubuntu@anditherobot.com
cd /var/www/tinyrisks.art
sudo cp tinyrisks.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tinyrisks
sudo systemctl start tinyrisks
sudo systemctl status tinyrisks  # Verify it's running
```

### 2. Install the nginx configuration

```bash
# Backup existing config first
sudo cp /etc/nginx/sites-available/tinyrisks.art /etc/nginx/sites-available/tinyrisks.art.backup

# Install new config
sudo cp nginx.conf /etc/nginx/sites-available/tinyrisks.art

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 3. Verify the fix

```bash
# Check Flask service status
sudo systemctl status tinyrisks

# Check Flask logs
tail -f /var/www/tinyrisks.art/logs/flask_stderr.log

# Test the admin endpoint
curl -I https://tinyrisks.art/admin
# Should return 302 (redirect to login) instead of 404

# Test after logging in
curl https://tinyrisks.art/login  # Access the login page
# Then manually test /admin in browser after logging in
```

## Verification

All existing tests pass, confirming:
- ✅ `/admin` route returns 302 (redirect) when not authenticated
- ✅ `/admin` route returns 200 when authenticated
- ✅ Authentication framework works correctly
- ✅ All other routes continue to work

## Future Deployments

Once the initial setup is complete, future deployments via GitHub Actions will automatically:
1. Pull the latest code
2. Install/update dependencies
3. Initialize the database
4. Restart the Flask service
5. Reload nginx

No additional manual intervention will be needed.

## Security Notes

- The default admin credentials are `admin` / `adminpass123`
- These should be changed immediately after the first login
- Flask-Login manages secure session cookies
- All traffic uses HTTPS with Let's Encrypt certificates
- The Flask app runs on localhost:5000 (not exposed externally)

