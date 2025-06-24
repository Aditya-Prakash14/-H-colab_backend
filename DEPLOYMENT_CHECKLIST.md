# HackMate Deployment Checklist

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment Checklist

### Code Preparation
- [ ] All code is committed to Git repository
- [ ] Repository is pushed to GitHub/GitLab/Bitbucket
- [ ] All deployment files are present:
  - [ ] `build.sh`
  - [ ] `requirements.txt` (updated with production dependencies)
  - [ ] `Procfile` (for Heroku)
  - [ ] `runtime.txt` (Python version)
  - [ ] Environment configuration files

### Django Configuration
- [ ] `SECRET_KEY` uses environment variable
- [ ] `DEBUG` is configurable via environment variable
- [ ] `ALLOWED_HOSTS` is configurable
- [ ] Database configuration supports `DATABASE_URL`
- [ ] Static files configuration is production-ready
- [ ] CORS settings are configured for production
- [ ] Security settings are enabled for production

### Database
- [ ] Database migrations are up to date
- [ ] Initial data population script exists
- [ ] Database backup strategy planned (for production)

## Render Deployment Checklist

### Database Setup
- [ ] PostgreSQL database created on Render
- [ ] Database credentials noted
- [ ] Internal Database URL copied

### Web Service Setup
- [ ] Web service created and connected to repository
- [ ] Build command set: `./build.sh`
- [ ] Start command set: `cd backend && gunicorn backend.wsgi:application`
- [ ] Environment variables configured:
  - [ ] `SECRET_KEY`
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS`
  - [ ] `DATABASE_URL`
  - [ ] `DJANGO_SUPERUSER_USERNAME`
  - [ ] `DJANGO_SUPERUSER_EMAIL`
  - [ ] `DJANGO_SUPERUSER_PASSWORD`

### Deployment
- [ ] Service deployed successfully
- [ ] Build logs checked for errors
- [ ] Application URL accessible
- [ ] Admin panel accessible
- [ ] API endpoints responding

## Post-Deployment Checklist

### Verification
- [ ] Application loads without errors
- [ ] Admin panel accessible with superuser credentials
- [ ] API endpoints return expected responses
- [ ] Database contains initial data
- [ ] Static files loading correctly

### API Testing
- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens are issued correctly
- [ ] Protected endpoints require authentication
- [ ] CORS headers present for frontend requests

### Frontend Configuration
- [ ] React Native app API URL updated
- [ ] Mobile app can connect to production API
- [ ] Authentication flow works end-to-end
- [ ] Data synchronization working

### Security
- [ ] HTTPS enabled (automatic on Render)
- [ ] Security headers present
- [ ] Admin credentials are secure
- [ ] Database credentials are secure
- [ ] No sensitive data in logs

### Performance
- [ ] Application response times acceptable
- [ ] Database queries optimized
- [ ] Static files served efficiently
- [ ] No memory leaks or excessive resource usage

### Monitoring
- [ ] Application logs accessible
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring set up (optional)
- [ ] Performance monitoring configured (optional)

## Troubleshooting Checklist

If deployment fails, check:

### Build Issues
- [ ] All dependencies in requirements.txt
- [ ] Python version compatibility
- [ ] Build script permissions (`chmod +x build.sh`)
- [ ] No syntax errors in Python code

### Runtime Issues
- [ ] Environment variables set correctly
- [ ] Database connection working
- [ ] Static files configuration
- [ ] CORS configuration
- [ ] Allowed hosts configuration

### Database Issues
- [ ] Database URL format correct
- [ ] Database accessible from application
- [ ] Migrations applied successfully
- [ ] Database user permissions correct

### Frontend Issues
- [ ] API URL updated in React Native app
- [ ] CORS origins include frontend domain
- [ ] API endpoints accessible from frontend
- [ ] Authentication headers configured correctly

## Quick Commands for Testing

### Test API Endpoints
```bash
# Health check
curl https://your-app-name.onrender.com/api/v1/

# Register user
curl -X POST https://your-app-name.onrender.com/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'

# Login
curl -X POST https://your-app-name.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### Check Logs
- Render: View logs in service dashboard
- Heroku: `heroku logs --tail`
- Docker: `docker-compose logs backend`

## Emergency Rollback

If deployment fails:

### Render
- Revert to previous deployment in dashboard
- Or push previous commit and redeploy

### Heroku
```bash
heroku rollback
```

### Docker
```bash
docker-compose down
git checkout previous-commit
docker-compose up -d
```

---

**Remember**: Always test in a staging environment before deploying to production!
