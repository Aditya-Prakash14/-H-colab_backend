# HackMate API Documentation

## Overview
HackMate is a Django REST API backend for a mobile app that helps users find and manage hackathon teammates.

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication

#### Register User
- **POST** `/auth/register/`
- **Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

#### Login
- **POST** `/auth/login/`
- **Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

#### Refresh Token
- **POST** `/auth/refresh/`
- **Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

### User Profile

#### Get/Update Current User Profile
- **GET/PUT/PATCH** `/profile/`
- **Response:**
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "bio": "Full-stack developer passionate about AI",
    "skills": ["Python", "React", "Machine Learning"],
    "experience_level": "intermediate",
    "github_url": "https://github.com/johndoe",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "location": "San Francisco, CA",
    "timezone": "America/Los_Angeles",
    "preferred_roles": ["developer", "backend_dev"],
    "is_available": true
}
```

#### Get Public User Profile
- **GET** `/profile/<username>/`

#### Get User Statistics
- **GET** `/stats/`

### Skills

#### List Skills
- **GET** `/skills/`
- **Query Parameters:**
  - `search`: Search by name or category
  - `ordering`: Order by name, category, or created_at

### Hackathons

#### List/Create Hackathons
- **GET/POST** `/hackathons/`
- **Query Parameters:**
  - `status`: Filter by status (upcoming, ongoing, completed)
  - `location_type`: Filter by location type (remote, onsite, hybrid)
  - `start_date`: Filter by start date (YYYY-MM-DD)
  - `end_date`: Filter by end date (YYYY-MM-DD)
  - `search`: Search in title, description, organizer

#### Get/Update/Delete Hackathon
- **GET/PUT/PATCH/DELETE** `/hackathons/<id>/`

### Teams

#### List/Create Teams
- **GET/POST** `/teams/`
- **Query Parameters:**
  - `hackathon`: Filter by hackathon ID
  - `is_recruiting`: Filter by recruiting status (true/false)
  - `my_teams`: Show only user's teams (true/false)
  - `search`: Search in name, description

#### Get/Update/Delete Team
- **GET/PUT/PATCH/DELETE** `/teams/<id>/`

#### Join Team
- **POST** `/teams/<id>/join/`
- **Body:**
```json
{
    "role": "developer"
}
```

#### Leave Team
- **POST** `/teams/<id>/leave/`

#### Invite to Team
- **POST** `/teams/<id>/invite/`
- **Body:**
```json
{
    "username": "targetuser",
    "role": "designer",
    "message": "We'd love to have you on our team!"
}
```

### Tasks

#### List/Create Tasks
- **GET/POST** `/tasks/`
- **Query Parameters:**
  - `team`: Filter by team ID
  - `assigned_to`: Filter by assigned user
  - `status`: Filter by status (todo, in_progress, review, done, blocked)
  - `priority`: Filter by priority (low, medium, high, urgent)
  - `my_tasks`: Show only user's assigned tasks (true/false)

#### Get/Update/Delete Task
- **GET/PUT/PATCH/DELETE** `/tasks/<id>/`

#### Task Comments
- **GET/POST** `/tasks/<id>/comments/`

### Matching System

#### Get/Update Matching Preferences
- **GET/PUT/PATCH** `/matching/preferences/`

#### Find Teammates
- **GET** `/matching/find-teammates/`
- Returns a list of compatible users with compatibility scores

## Response Format

### Success Response
```json
{
    "data": {...},
    "message": "Success message"
}
```

### Error Response
```json
{
    "error": "Error message",
    "details": {...}
}
```

## Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting
Currently no rate limiting is implemented, but it's recommended for production.

## CORS
CORS is configured to allow requests from React Native/Expo development servers.

## Database
The API supports both PostgreSQL (recommended for production) and SQLite (for development).
Set `USE_SQLITE=true` in your `.env` file to use SQLite.
