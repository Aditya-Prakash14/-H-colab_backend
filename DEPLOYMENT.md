# HackMate Deployment Guide

This guide provides step-by-step instructions for deploying the HackMate application to various platforms.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Render Deployment (Recommended)](#render-deployment-recommended)
3. [Docker Deployment](#docker-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment Setup](#post-deployment-setup)

## Prerequisites

- Git repository with your HackMate code
- Python 3.11+ installed locally
- Node.js and npm/yarn for React Native development

## Render Deployment (Recommended)

Render is a modern cloud platform that simplifies deployment with automatic builds and managed databases.

### Step 1: Prepare Your Repository

1. Ensure your code is pushed to GitHub, GitLab, or Bitbucket
2. Make sure all files from this deployment setup are committed:
   - `build.sh`
   - `requirements.txt` (updated)
   - Environment configuration files
   - Updated Django settings

### Step 2: Create Render Account

1. Sign up at [render.com](https://render.com)
2. Connect your Git provider (GitHub/GitLab)

### Step 3: Create PostgreSQL Database

1. In Render dashboard, click "New PostgreSQL"
2. Configure:
   - **Name**: `hackmate-db`
   - **Database**: `hackmate_db`
   - **User**: `hackmate_user`
   - **Region**: Choose closest to your users
   - **Instance Type**: Free tier or paid based on needs
3. Click "Create Database"
4. Note the **Internal Database URL** for later use

### Step 4: Create Web Service

1. Click "New Web Service"
2. Connect your repository
3. Configure:
   - **Name**: `hackmate-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && gunicorn backend.wsgi:application`
   - **Instance Type**: Free tier or paid

### Step 5: Set Environment Variables

In the Environment section, add:

```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://user:password@host:port/database
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@hackmate.com
DJANGO_SUPERUSER_PASSWORD=secure-admin-password
```

**Important**: Replace the DATABASE_URL with the Internal Database URL from Step 3.

### Step 6: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any errors

### Step 7: Verify Deployment

1. Visit your app URL: `https://your-app-name.onrender.com`
2. Check API endpoints: `https://your-app-name.onrender.com/api/v1/`
3. Access admin panel: `https://your-app-name.onrender.com/admin/`

## Docker Deployment

For VPS or local deployment using Docker.

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Copy environment file**:
   ```bash
   cp .env.production .env
   # Edit .env with your production settings
   ```

2. **Build and start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   docker-compose exec backend python manage.py populate_initial_data
   ```

4. **Access application**:
   - Application: http://localhost
   - Admin: http://localhost/admin/

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account

### Steps

1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Run migrations**:
   ```bash
   heroku run python backend/manage.py migrate
   heroku run python backend/manage.py createsuperuser
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `yourdomain.com,www.yourdomain.com` |
| `DATABASE_URL` | Database connection URL | `postgresql://user:pass@host:port/db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | Production domain |
| `SECURE_SSL_REDIRECT` | Force HTTPS redirect | `True` |
| `DJANGO_SUPERUSER_USERNAME` | Auto-create superuser | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Superuser email | `admin@hackmate.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Superuser password | Required for auto-creation |

## Post-Deployment Setup

### 1. Verify API Endpoints

Test key endpoints:
- `GET /api/v1/hackathons/` - List hackathons
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login

### 2. Configure React Native App

Update `react-native/HackMate/src/constants/config.js`:

```javascript
export const API_BASE_URL = 'https://your-app-name.onrender.com/api/v1';
```

### 3. Test Mobile App

1. Update API URL in React Native app
2. Test registration and login
3. Verify data synchronization

### 4. Set Up Monitoring

- Monitor application logs
- Set up error tracking (Sentry recommended)
- Configure uptime monitoring

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check build logs in Render dashboard
   - Verify all dependencies in requirements.txt
   - Ensure build.sh has correct permissions

2. **Database Connection Issues**:
   - Verify DATABASE_URL is correct
   - Check database is running and accessible
   - Ensure database user has proper permissions

3. **Static Files Not Loading**:
   - Verify STATIC_ROOT and STATIC_URL settings
   - Check WhiteNoise configuration
   - Run collectstatic command

4. **CORS Issues**:
   - Update CORS_ALLOWED_ORIGINS
   - Check frontend API URL configuration
   - Verify HTTPS/HTTP protocol matching

### Getting Help

- Check application logs in your platform dashboard
- Review Django error logs
- Test API endpoints with tools like Postman
- Verify environment variables are set correctly

## Security Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG is set to False
- [ ] ALLOWED_HOSTS is properly configured
- [ ] Database credentials are secure
- [ ] HTTPS is enabled
- [ ] CORS is properly configured
- [ ] Admin credentials are strong

## Performance Optimization

- Use a CDN for static files
- Enable database connection pooling
- Configure caching (Redis recommended)
- Monitor and optimize database queries
- Set up proper logging and monitoring

---

For additional help or questions, refer to the API documentation in `backend/API_DOCUMENTATION.md`.
