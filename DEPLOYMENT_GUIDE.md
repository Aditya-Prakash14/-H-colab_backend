# HackMate Backend - Render Deployment Guide

## 🚀 Quick Fix for Python 3.13 Compatibility Issue

### Problem
You're encountering a Python 3.13 compatibility issue with Pillow and other packages during Render deployment.

### ✅ Solution (Files Already Created)

I've created the necessary files to fix this issue:

1. **`runtime.txt`** - Specifies Python 3.11.9 for Render
2. **Updated `requirements.txt`** - Fixed Pillow version and added production dependencies
3. **`render.yaml`** - Complete Render deployment configuration

### 📋 Deployment Steps

#### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix Python version and add Render deployment config"
git push origin main
```

#### Step 2: Deploy on Render

1. **Go to Render Dashboard** (https://dashboard.render.com)
2. **Select your web service**
3. **Click "Manual Deploy"**
4. **Select "Clear cache and deploy"**

#### Step 3: Set Environment Variables (if not using render.yaml)

If you're not using the `render.yaml` file, manually set these environment variables in Render:

```
DEBUG=False
USE_SQLITE=False
PYTHON_VERSION=3.11.9
SECRET_KEY=your-secret-key-here
```

### 🔧 Alternative: Manual Render Setup

If you prefer manual setup instead of using `render.yaml`:

#### 1. Create Web Service
- **Build Command**: 
  ```bash
  cd backend && pip install -r ../requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command**: 
  ```bash
  cd backend && gunicorn backend.wsgi:application
  ```

#### 2. Create PostgreSQL Database
- Add a PostgreSQL database in Render
- Note the connection details

#### 3. Environment Variables
Set these in your Render web service:
```
DEBUG=False
USE_SQLITE=False
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
```

### 📁 Files Created for Deployment

#### `runtime.txt`
```
python-3.11.9
```

#### Updated `requirements.txt`
- Fixed Pillow version to `10.3.0`
- Added production dependencies:
  - `gunicorn==21.2.0`
  - `whitenoise==6.6.0`
  - `dj-database-url==2.1.0`

#### `render.yaml` (Complete Configuration)
- Automated deployment configuration
- Database setup included
- Environment variables configured

### 🔍 Troubleshooting

#### If deployment still fails:

1. **Check Build Logs** in Render dashboard
2. **Verify Python Version** in logs (should show 3.11.9)
3. **Check Database Connection** - ensure DATABASE_URL is set correctly

#### Common Issues:

**Issue**: Static files not loading
**Solution**: Ensure `STATIC_ROOT` and `STATICFILES_STORAGE` are configured (already done)

**Issue**: Database connection errors
**Solution**: Check DATABASE_URL format and database credentials

**Issue**: CORS errors from frontend
**Solution**: Update `CORS_ALLOWED_ORIGINS` in settings.py with your frontend URL

### 🎯 Expected Result

After successful deployment:
- ✅ Python 3.11.9 will be used (compatible with all packages)
- ✅ Pillow will install correctly
- ✅ PostgreSQL database will be connected
- ✅ Static files will be served properly
- ✅ API will be accessible at your Render URL

### 📱 Frontend Integration

Once deployed, update your React Native app to use the Render URL:

```javascript
const API_BASE_URL = 'https://your-app-name.onrender.com/api/v1';
```

### 🔐 Security Notes

For production:
1. **Generate a new SECRET_KEY** and set it in environment variables
2. **Update ALLOWED_HOSTS** to include your Render domain
3. **Set DEBUG=False** in production
4. **Configure proper CORS origins** for your frontend domain

### 📞 Support

If you continue to have issues:
1. Check the Render build logs for specific error messages
2. Ensure all environment variables are set correctly
3. Verify the database connection string format

The deployment should now work correctly with Python 3.11.9! 🎉
