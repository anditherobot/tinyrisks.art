# Quick Start: Fixing the /admin 404 Error

## TL;DR

The `/admin` endpoint returns 404 because the Flask app isn't running. Run these commands on your production server to fix it:

```bash
# SSH into the server
ssh ubuntu@anditherobot.com

# Navigate to the project
cd /var/www/tinyrisks.art

# Pull the latest changes (includes config files)
git pull origin master

# Install dependencies in virtual environment
if [ ! -d venv ]; then python3 -m venv venv; fi
./venv/bin/pip install -r requirements.txt

# Verify gunicorn installed successfully
./venv/bin/gunicorn --version || { echo "Gunicorn installation failed. Check requirements.txt and pip output."; exit 1; }

# Create logs directory (for nginx and other logs, not Flask)
mkdir -p logs

# Install systemd service
sudo cp tinyrisks.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tinyrisks
sudo systemctl start tinyrisks

# Verify Flask is running
sudo systemctl status tinyrisks

# Install nginx config
sudo cp /etc/nginx/sites-available/tinyrisks.art /etc/nginx/sites-available/tinyrisks.art.backup
sudo cp nginx.conf /etc/nginx/sites-available/tinyrisks.art

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx

# Test the fix
curl -I https://tinyrisks.art/admin
# Should return 302 (redirect to /login) instead of 404
```

## What This Does

1. **Installs Gunicorn** - Production WSGI server for Flask
2. **Creates systemd service** - Runs Flask app automatically on boot
3. **Configures nginx** - Proxies requests to Flask instead of serving static files only

## After Setup

- `/admin` will redirect to `/login` (requires authentication)
- Login with the admin credentials configured during database initialization
- **Security Note:** Change the default admin password immediately after first login
- Future deployments will automatically restart the Flask service

## Troubleshooting

**Flask service won't start:**
```bash
sudo journalctl -u tinyrisks -n 50
```

**Still getting 404:**
```bash
# Check if Flask is running
sudo systemctl status tinyrisks

# Check if nginx config is correct
sudo nginx -t

# Check nginx logs
sudo tail /var/log/nginx/tinyrisks.art.error.log
```

## More Information

- Full setup guide: `INSTALLATION.md`
- Detailed fix explanation: `FIX_SUMMARY.md`
- Infrastructure overview: `INFRASTRUCTURE.md`

