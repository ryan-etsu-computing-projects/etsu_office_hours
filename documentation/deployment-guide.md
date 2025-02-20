# ETSU Office Hours Directory System - Docker Deployment Guide

This guide explains how to deploy the ETSU Office Hours application using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your server
- Domain name (if deploying to production)
- Basic knowledge of the command line

## Deployment Steps

### 1. Prepare the Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd etsu_office_hours
   ```

2. Create environment variables file:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with secure values:
   ```bash
   nano .env
   ```
   - Generate a secure Django secret key:
     ```python
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```
   - Generate a secure encryption key:
     ```python
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   - Set strong database password and other variables

### 2. Set Up SSL Certificates

For development/testing:
```bash
chmod +x generate-ssl.sh
./generate-ssl.sh
```

For production:
1. Obtain SSL certificates from a trusted certificate authority or Let's Encrypt
2. Place your certificate files in `nginx/ssl/`:
   - `cert.pem`: Certificate file
   - `key.pem`: Private key file

### 3. Build and Start the Services

```bash
docker-compose up -d --build
```

This command builds the Docker images and starts all services in detached mode.

### 4. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 5. Verify Deployment

Access your application at:
- https://your-domain.com (production)
- https://localhost (local development)

### Maintenance Tasks

#### View Logs
```bash
docker-compose logs -f web
```

#### Database Backup
```bash
docker-compose exec db pg_dump -U postgres etsu_office_hours > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Database Restore
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres etsu_office_hours
```

#### Update Application
```bash
git pull
docker-compose down
docker-compose up -d --build
```

#### Run Management Commands
```bash
docker-compose exec web python manage.py check_inactive_users
```

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL logs: `docker-compose logs db`
- Verify database credentials in `.env`
- Ensure database volume is properly mounted

### Application Not Starting
- Check Django logs: `docker-compose logs web`
- Verify all environment variables are set correctly
- Check permissions on directories

### SSL Certificate Issues
- Verify certificate paths in nginx configuration
- Check certificate validity: `openssl x509 -in nginx/ssl/cert.pem -text -noout`

## Security Considerations

- Regularly update all containers
- Monitor application logs for suspicious activity
- Use strong, unique passwords
- Change SSL certificates before they expire
- Implement regular backups
- Consider using Docker Secrets for sensitive information in production
