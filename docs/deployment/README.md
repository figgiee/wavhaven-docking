# WAVHaven Deployment Guide

## Overview

This guide covers the deployment process for WAVHaven, including server setup, Docker configuration, and monitoring.

## Prerequisites

- Docker and Docker Compose
- AWS Account with S3 access
- Domain name and SSL certificate
- Stripe account for payments
- PostgreSQL database
- Redis server
- SMTP server for emails

## Environment Setup

1. Create `.env` file:

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
DEBUG=False

# Database
DB_NAME=wavhaven
DB_USER=wavhaven_user
DB_PASSWORD=your-db-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region

# Stripe
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret

# Email
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
```

## Docker Configuration

1. Production Docker Compose (`docker-compose.prod.yml`):

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    networks:
      - wavhaven_net

  postgres:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    networks:
      - wavhaven_net

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    networks:
      - wavhaven_net

  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A config worker -l INFO
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    networks:
      - wavhaven_net

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A config beat -l INFO
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    networks:
      - wavhaven_net

  nginx:
    image: nginx:1.21-alpine
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./nginx/prod:/etc/nginx/conf.d
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    networks:
      - wavhaven_net

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  wavhaven_net:
    driver: bridge
```

2. Production Dockerfile (`Dockerfile.prod`):

```dockerfile
# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE config.settings.production

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . .

RUN python manage.py collectstatic --noinput

USER nobody
```

## Nginx Configuration

Create `nginx/prod/wavhaven.conf`:

```nginx
upstream wavhaven {
    server web:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;

    client_max_body_size 50M;

    location / {
        proxy_pass http://wavhaven;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public, no-transform";
    }

    location /ws/ {
        proxy_pass http://wavhaven;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Deployment Steps

1. Initial Setup:
```bash
# Clone repository
git clone https://github.com/yourusername/wavhaven.git
cd wavhaven

# Create necessary directories
mkdir -p nginx/prod certbot/conf certbot/www

# Copy environment template
cp .env.example .env
# Edit .env with production values
```

2. SSL Certificate:
```bash
# Start nginx for initial certificate
docker-compose -f docker-compose.prod.yml up -d nginx
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d your-domain.com
```

3. Start Services:
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Monitoring

1. Setup Prometheus monitoring:
```bash
# Install django-prometheus
pip install django-prometheus

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'django_prometheus',
]

# Add to urls.py
urlpatterns = [
    ...
    path('metrics/', include('django_prometheus.urls')),
]
```

2. Configure Grafana dashboards for:
- Request latency
- Database query performance
- Cache hit rates
- Error rates
- System metrics

## Backup Strategy

1. Database Backups:
```bash
# Daily backups
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U $DB_USER $DB_NAME
```

2. Media Backups:
- AWS S3 versioning enabled
- Regular sync of local media to S3

## Security Checklist

- [ ] SSL/TLS configured
- [ ] Security headers set
- [ ] Django security settings verified
- [ ] Database access restricted
- [ ] Redis password set
- [ ] Admin access limited by IP
- [ ] Regular security updates
- [ ] File upload validation
- [ ] Rate limiting configured
- [ ] CORS settings reviewed

## Troubleshooting

1. Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f [service]
```

2. Common issues:
- Database connection errors
- Static files not serving
- SSL certificate issues
- Redis connection problems
- Celery task failures

## Performance Optimization

1. Django:
- Configure caching
- Optimize database queries
- Use debug toolbar in development

2. Nginx:
- Enable gzip compression
- Configure microcaching
- Optimize SSL settings

3. Database:
- Regular vacuum
- Index optimization
- Connection pooling

## Maintenance

1. Regular tasks:
- SSL certificate renewal
- Database backups
- Log rotation
- Security updates
- Performance monitoring

2. Update procedure:
```bash
# Pull latest changes
git pull origin main

# Build new images
docker-compose -f docker-compose.prod.yml build

# Apply migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Restart services
docker-compose -f docker-compose.prod.yml up -d
``` 