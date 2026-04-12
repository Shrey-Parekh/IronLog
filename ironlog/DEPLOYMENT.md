# IronLog Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Domain name (for production)
- SSL certificate (recommended: Let's Encrypt)

## Production Deployment

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and set:
- `POSTGRES_PASSWORD`: Strong database password
- `SECRET_KEY`: Random 32+ character string
- `CORS_ORIGINS`: Your domain(s)
- `PORT`: Port for frontend (default: 80)

### 2. Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.yml build

# Start all services
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

### 3. Run Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.yml exec backend alembic upgrade head

# Seed exercise database
docker-compose -f docker-compose.yml exec backend python -m app.seed.seed_db
```

### 4. Verify Deployment

Check service health:

```bash
# Check all services
docker-compose -f docker-compose.yml ps

# Check logs
docker-compose -f docker-compose.yml logs -f

# Test backend health
curl http://localhost/api/health

# Test frontend
curl http://localhost/health
```

## SSL/HTTPS Setup (Recommended)

### Using Let's Encrypt with Certbot

1. Install Certbot:
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. Get certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. Update nginx.conf to use SSL (certbot does this automatically)

4. Set up auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.yml logs -f

# Specific service
docker-compose -f docker-compose.yml logs -f backend
docker-compose -f docker-compose.yml logs -f celery-worker
```

### Health Checks

All services have health checks configured:
- Backend: `http://localhost/api/health`
- Frontend: `http://localhost/health`
- PostgreSQL: Built-in pg_isready
- Redis: Built-in redis-cli ping

## Backup

### Database Backup

```bash
# Create backup
docker-compose -f docker-compose.yml exec postgres pg_dump -U ironlog ironlog > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose -f docker-compose.yml exec -T postgres psql -U ironlog ironlog < backup_20240101.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v ironlog_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
docker run --rm -v ironlog_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz /data
```

## Scaling

### Scale Celery Workers

```bash
docker-compose -f docker-compose.yml up -d --scale celery-worker=4
```

### Scale Backend

Update docker-compose.yml to add more backend replicas and use a load balancer.

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.yml logs service_name

# Restart service
docker-compose -f docker-compose.yml restart service_name

# Rebuild service
docker-compose -f docker-compose.yml up -d --build service_name
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.yml exec postgres pg_isready

# Check connection from backend
docker-compose -f docker-compose.yml exec backend python -c "from app.database import engine; print('Connected')"
```

### Clear Redis Cache

```bash
docker-compose -f docker-compose.yml exec redis redis-cli FLUSHALL
```

## Updating

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.yml up -d --build

# Run migrations
docker-compose -f docker-compose.yml exec backend alembic upgrade head
```

### Update Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..

# Rebuild images
docker-compose -f docker-compose.yml build
```

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (only expose ports 80, 443)
- [ ] Set up regular backups
- [ ] Enable Docker security scanning
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets (never commit)
- [ ] Implement rate limiting (nginx)
- [ ] Set up monitoring/alerting

## Performance Optimization

### Backend

- Adjust Gunicorn workers based on CPU cores: `workers = (2 * cpu_cores) + 1`
- Enable connection pooling in database
- Use Redis for caching frequently accessed data

### Frontend

- Nginx gzip compression is enabled
- Static assets are cached for 1 year
- Service worker caches API responses

### Database

- Regular VACUUM and ANALYZE
- Add indexes for frequently queried columns
- Monitor slow queries

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health checks
- Consult application documentation
