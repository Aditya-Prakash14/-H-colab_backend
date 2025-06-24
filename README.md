# HackMate - Django Backend

HackMate is a comprehensive Django REST API backend for a mobile app that helps users find and manage hackathon teammates. The platform supports user authentication, profile management, hackathon listings, team formation, task management, and an intelligent teammate matching system.

## Features

### ✅ Completed Features

#### Core Features
- **JWT Authentication**: Secure user registration, login, and token refresh
- **User Profile Management**: Extended profiles with skills, bio, GitHub/LinkedIn links, experience levels
- **Hackathon Listings**: Create and browse hackathons with filtering by location, date, and status
- **Team Management**: Create teams, join/leave teams, assign roles (Developer, Designer, PM, etc.)
- **Task Management**: Create, assign, and track tasks with deadlines, priorities, and status updates
- **Teammate Matching System**: Algorithm-based matching using skills and preferences

#### Advanced Features
- **Team Invitations**: Send, receive, accept/decline team invitations
- **Team Dashboard**: Comprehensive team analytics and member management
- **Team Health Scoring**: Algorithm to assess team performance and activity
- **Leadership Transfer**: Transfer team leadership between members
- **User Recommendations**: Personalized hackathon and team recommendations
- **Trending Skills**: Track and display popular skills across the platform
- **User Search**: Search for users by name, username, or skills
- **Activity Tracking**: Monitor user activity and engagement metrics
- **Hackathon Analytics**: Detailed analytics for hackathon organizers

#### Technical Features
- **CORS Support**: Configured for React Native + Expo frontend communication
- **Database Support**: PostgreSQL (production) and SQLite (development)
- **Admin Interface**: Django admin for managing all models
- **API Documentation**: Comprehensive endpoint documentation
- **Testing Suite**: Unit tests for key functionality
- **API Testing Script**: Automated testing script for all endpoints

### 🔧 Technical Stack

- **Framework**: Django 5.2.3 + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (recommended) / SQLite (development)
- **Image Handling**: Pillow for profile pictures and hackathon banners
- **CORS**: django-cors-headers for frontend communication

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Django_react-mongo
```

2. **Create virtual environment**
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
# Copy the example .env file
cp backend/.env.example backend/.env

# Edit backend/.env with your settings
# For development, you can use SQLite by setting USE_SQLITE=true
```

5. **Database Setup**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_initial_data
```

6. **Run the server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
USE_SQLITE=true  # Set to false for PostgreSQL

# PostgreSQL Configuration (if not using SQLite)
DB_NAME=hackmate_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/refresh/` - Token refresh

### User Management
- `GET/PUT/PATCH /api/v1/profile/` - Current user profile
- `GET /api/v1/profile/<username>/` - Public user profile
- `GET /api/v1/stats/` - User statistics

### Hackathons
- `GET/POST /api/v1/hackathons/` - List/create hackathons
- `GET/PUT/PATCH/DELETE /api/v1/hackathons/<id>/` - Hackathon details

### Teams
- `GET/POST /api/v1/teams/` - List/create teams
- `GET/PUT/PATCH/DELETE /api/v1/teams/<id>/` - Team details
- `POST /api/v1/teams/<id>/join/` - Join team
- `POST /api/v1/teams/<id>/leave/` - Leave team
- `POST /api/v1/teams/<id>/invite/` - Invite to team

### Tasks
- `GET/POST /api/v1/tasks/` - List/create tasks
- `GET/PUT/PATCH/DELETE /api/v1/tasks/<id>/` - Task details
- `GET/POST /api/v1/tasks/<id>/comments/` - Task comments

### Matching System
- `GET/PUT/PATCH /api/v1/matching/preferences/` - Matching preferences
- `GET /api/v1/matching/find-teammates/` - Find compatible teammates

### Advanced Features
- `GET /api/v1/recommendations/` - Get personalized recommendations
- `GET /api/v1/activity/` - Get user activity summary
- `GET /api/v1/search/users/` - Search for users
- `GET /api/v1/skills/trending/` - Get trending skills
- `GET /api/v1/hackathons/<id>/analytics/` - Get hackathon analytics
- `GET /api/v1/teams/<id>/health/` - Get team health score
- `POST /api/v1/teams/<id>/transfer-leadership/` - Transfer team leadership
- `GET /api/v1/invitations/` - Get user's pending invitations
- `POST /api/v1/invitations/<id>/respond/` - Respond to team invitation
- `POST /api/v1/tasks/<id>/assign/` - Assign task to team member

### Other
- `GET /api/v1/skills/` - List available skills

## Testing

Run the test suite:
```bash
cd backend
python manage.py test
```

## Database Models

### Core Models
- **UserProfile**: Extended user information with skills and preferences
- **Skill**: Predefined skills categorized by type
- **Hackathon**: Event information with dates and requirements
- **Team**: Team formation with member management
- **TeamMembership**: User roles within teams
- **Task**: Task management with assignments and deadlines
- **MatchingPreference**: User preferences for teammate matching

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` using your superuser credentials to manage:
- Users and profiles
- Hackathons
- Teams and memberships
- Tasks and comments
- Skills and matching preferences

## API Documentation

Detailed API documentation is available in `backend/API_DOCUMENTATION.md`

## Development

### Adding New Features

1. Create models in `api/models.py`
2. Create serializers in `api/serializers.py`
3. Create views in `api/views.py`
4. Add URL patterns in `api/urls.py`
5. Write tests in `api/tests.py`
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to classes and methods
- Write tests for new functionality

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up proper CORS origins
4. Use environment variables for sensitive data
5. Configure static/media file serving
6. Set up proper logging
7. Use a production WSGI server (gunicorn, uWSGI)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
