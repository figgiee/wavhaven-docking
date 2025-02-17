# WavHaven Deployment Guide

This guide covers the deployment process for WavHaven in both development and production environments.

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend assets)
- Git

### Environment Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/wavhaven.git
cd wavhaven
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN_WHITELIST=http://localhost:8000
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Production Deployment

### Prerequisites
- PostgreSQL
- Nginx
- Gunicorn
- Redis (for caching)
- SSL certificate
- Domain name

### Server Setup (Ubuntu 20.04+)

1. Update system and install dependencies:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql nginx redis-server
```

2. Create PostgreSQL database:
```bash
sudo -u postgres psql
CREATE DATABASE wavhaven;
CREATE USER wavhaven_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE wavhaven TO wavhaven_user;
\q
```

3. Clone and setup application:
```bash
cd /var/www
git clone https://github.com/yourusername/wavhaven.git
cd wavhaven
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
nano .env
```

Add production settings:
```env
DEBUG=False
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgres://wavhaven_user:your_password@localhost:5432/wavhaven
ALLOWED_HOSTS=your-domain.com
STATIC_ROOT=/var/www/wavhaven/staticfiles
MEDIA_ROOT=/var/www/wavhaven/media
REDIS_URL=redis://localhost:6379/1
```

5. Setup Gunicorn:
Create systemd service file:
```bash
sudo nano /etc/systemd/system/wavhaven.service
```

Add configuration:
```ini
[Unit]
Description=WavHaven Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/wavhaven
ExecStart=/var/www/wavhaven/venv/bin/gunicorn config.wsgi:application \
    --workers 3 \
    --bind unix:/var/www/wavhaven/wavhaven.sock \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log

[Install]
WantedBy=multi-user.target
```

6. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/wavhaven
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/wavhaven;
    }

    location /media/ {
        root /var/www/wavhaven;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/wavhaven/wavhaven.sock;
    }
}
```

7. Enable site and restart services:
```bash
sudo ln -s /etc/nginx/sites-available/wavhaven /etc/nginx/sites-enabled
sudo systemctl start wavhaven
sudo systemctl enable wavhaven
sudo systemctl restart nginx
```

8. Setup SSL with Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### File Storage

For production, configure AWS S3 or similar for media file storage:

1. Install boto3:
```bash
pip install boto3
```

2. Add S3 settings to .env:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

### Monitoring

1. Install monitoring tools:
```bash
pip install sentry-sdk
```

2. Add Sentry configuration to settings.py:
```python
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Backup

1. Setup automated PostgreSQL backups:
```bash
sudo nano /etc/cron.daily/backup-wavhaven
```

Add backup script:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/wavhaven"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
pg_dump wavhaven | gzip > "$BACKUP_DIR/wavhaven_$TIMESTAMP.sql.gz"
```

2. Make script executable:
```bash
sudo chmod +x /etc/cron.daily/backup-wavhaven
```

### Security Considerations

1. Configure firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

2. Set secure permissions:
```bash
sudo chown -R www-data:www-data /var/www/wavhaven
sudo chmod -R 755 /var/www/wavhaven
```

3. Regular updates:
```bash
sudo apt update
sudo apt upgrade
pip install --upgrade -r requirements.txt
```

## Maintenance

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic --no-input
```

### Clearing Cache
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Monitoring Logs
```bash
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/error.log
``` 