# Installation Instructions for Flask Application

This document explains how to set up the Flask application with nginx and systemd on your server.

## Prerequisites

- Ubuntu 22.04 LTS (or similar)
- nginx installed
- Python 3.7+
- sudo access

## Installation Steps

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip nginx
```

### 2. Set Up the Application

**Option A: System-wide installation (simpler)**

```bash
# Navigate to the application directory
cd /var/www/tinyrisks.art

# Install Python dependencies (including gunicorn for production)
pip3 install -r requirements.txt

# Create logs directory
mkdir -p logs

# Initialize the database
python3 init_db.py
```

**Option B: Virtual environment (recommended for production)**

```bash
# Navigate to the application directory
cd /var/www/tinyrisks.art

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Initialize the database
python3 init_db.py

# If using a virtual environment, update tinyrisks.service to use:
# ExecStart=/var/www/tinyrisks.art/venv/bin/python3 -m gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### 3. Install Systemd Service

```bash
# Copy the service file
sudo cp tinyrisks.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable tinyrisks

# Start the service
sudo systemctl start tinyrisks

# Check status
sudo systemctl status tinyrisks
```

### 4. Install Nginx Configuration

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/tinyrisks.art

# Create symbolic link to enable the site
sudo ln -sf /etc/nginx/sites-available/tinyrisks.art /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 5. Set File Permissions

```bash
# Ensure www-data can access application files
sudo chown -R www-data:www-data /var/www/tinyrisks.art/htdocs/
sudo chown -R www-data:www-data /var/www/tinyrisks.art/logs/
```

## Verification

### Check Flask App Status

```bash
sudo systemctl status tinyrisks
```

### View Flask Logs

```bash
# Standard output
tail -f /var/www/tinyrisks.art/logs/flask_stdout.log

# Error output
tail -f /var/www/tinyrisks.art/logs/flask_stderr.log
```

### Test the Application

```bash
# Test local Flask app
curl http://localhost:5000/

# Test through nginx
curl https://tinyrisks.art/
```

## Troubleshooting

### Flask App Won't Start

Check the logs:
```bash
sudo journalctl -u tinyrisks -n 50 --no-pager
tail -f /var/www/tinyrisks.art/logs/flask_stderr.log
```

Common issues:
- Missing Python dependencies: `pip3 install -r requirements.txt` (installs Flask, gunicorn, Flask-Login)
- Database not initialized: `python3 init_db.py`
- Port 5000 already in use: Check with `sudo lsof -i :5000`
- Gunicorn module not found: Ensure all dependencies are installed with `pip3 install -r requirements.txt`

### Nginx 404 Errors

- Ensure Flask app is running: `sudo systemctl status tinyrisks`
- Check nginx error log: `sudo tail /var/log/nginx/error.log`
- Verify proxy settings in `/etc/nginx/sites-available/tinyrisks.art`

### Admin Page 401/Redirect to Login

This is expected behavior! The `/admin` route requires authentication. Navigate to `/login` first to log in with the admin credentials.

Default credentials:
- Username: `admin`
- Password: `adminpass123`

## Updating the Application

When deploying new code:

```bash
cd /var/www/tinyrisks.art
git pull origin master
pip3 install -r requirements.txt  # Update dependencies if changed
python3 init_db.py  # Safe to run - won't overwrite existing data
sudo systemctl restart tinyrisks
sudo systemctl reload nginx
```

## Security Notes

- Change the default admin password after first login
- Set a secure `SECRET_KEY` environment variable in production
- Keep SSL certificates up to date (certbot handles this automatically)
- Regularly update system packages and Python dependencies

