#!/usr/bin/env python
"""
Comprehensive API testing script for HackMate backend
Run this script to test all major API endpoints
"""

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.test_data = {}
    
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
    
    def make_request(self, method, endpoint, data=None, auth=True):
        """Make HTTP request with optional authentication"""
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            return response
        except requests.exceptions.ConnectionError:
            self.log("Connection error. Make sure the Django server is running.", "ERROR")
            return None
    
    def test_user_registration(self):
        """Test user registration"""
        self.log("Testing user registration...")
        
        data = {
            "username": "testuser123",
            "email": "test@hackmate.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
            "password_confirm": "testpassword123"
        }
        
        response = self.make_request('POST', '/auth/register/', data, auth=False)
        if response and response.status_code == 201:
            self.log("✓ User registration successful")
            return True
        else:
            self.log(f"✗ User registration failed: {response.status_code if response else 'No response'}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        self.log("Testing user login...")
        
        data = {
            "username": "testuser123",
            "password": "testpassword123"
        }
        
        response = self.make_request('POST', '/auth/login/', data, auth=False)
        if response and response.status_code == 200:
            response_data = response.json()
            self.access_token = response_data.get('access')
            self.refresh_token = response_data.get('refresh')
            self.log("✓ User login successful")
            return True
        else:
            self.log(f"✗ User login failed: {response.status_code if response else 'No response'}")
            return False
    
    def test_profile_management(self):
        """Test profile management"""
        self.log("Testing profile management...")
        
        # Get profile
        response = self.make_request('GET', '/profile/')
        if response and response.status_code == 200:
            self.log("✓ Get profile successful")
            profile_data = response.json()
            self.user_id = profile_data['user']['id']
        else:
            self.log("✗ Get profile failed")
            return False
        
        # Update profile
        update_data = {
            "bio": "Test user for API testing",
            "skills": ["Python", "Django", "React"],
            "experience_level": "intermediate",
            "github_url": "https://github.com/testuser",
            "location": "San Francisco, CA"
        }
        
        response = self.make_request('PATCH', '/profile/', update_data)
        if response and response.status_code == 200:
            self.log("✓ Update profile successful")
            return True
        else:
            self.log("✗ Update profile failed")
            return False
    
    def test_hackathon_operations(self):
        """Test hackathon operations"""
        self.log("Testing hackathon operations...")
        
        # List hackathons
        response = self.make_request('GET', '/hackathons/')
        if response and response.status_code == 200:
            self.log("✓ List hackathons successful")
            hackathons = response.json()['results'] if 'results' in response.json() else response.json()
            if hackathons:
                self.test_data['hackathon_id'] = hackathons[0]['id']
        else:
            self.log("✗ List hackathons failed")
            return False
        
        # Create hackathon
        future_date = datetime.now() + timedelta(days=30)
        hackathon_data = {
            "title": "Test Hackathon API",
            "description": "A test hackathon created via API",
            "short_description": "API test hackathon",
            "location_type": "remote",
            "start_date": future_date.isoformat(),
            "end_date": (future_date + timedelta(days=2)).isoformat(),
            "registration_deadline": (future_date - timedelta(days=5)).isoformat(),
            "organizer": "API Tester",
            "themes": ["Testing", "API"],
            "required_skills": ["Python", "Django"]
        }
        
        response = self.make_request('POST', '/hackathons/', hackathon_data)
        if response and response.status_code == 201:
            self.log("✓ Create hackathon successful")
            self.test_data['created_hackathon_id'] = response.json()['id']
            return True
        else:
            self.log(f"✗ Create hackathon failed: {response.text if response else 'No response'}")
            return False
    
    def test_team_operations(self):
        """Test team operations"""
        self.log("Testing team operations...")
        
        if 'hackathon_id' not in self.test_data:
            self.log("✗ No hackathon available for team testing")
            return False
        
        # Create team
        team_data = {
            "name": "API Test Team",
            "description": "A team created for API testing",
            "hackathon": self.test_data['hackathon_id'],
            "max_members": 4,
            "required_skills": ["Python", "React"]
        }
        
        response = self.make_request('POST', '/teams/', team_data)
        if response and response.status_code == 201:
            self.log("✓ Create team successful")
            self.test_data['team_id'] = response.json()['id']
        else:
            self.log("✗ Create team failed")
            return False
        
        # Get team dashboard
        if 'team_id' in self.test_data:
            response = self.make_request('GET', f'/teams/{self.test_data["team_id"]}/dashboard/')
            if response and response.status_code == 200:
                self.log("✓ Get team dashboard successful")
            else:
                self.log("✗ Get team dashboard failed")
        
        return True
    
    def test_task_operations(self):
        """Test task operations"""
        self.log("Testing task operations...")
        
        if 'team_id' not in self.test_data:
            self.log("✗ No team available for task testing")
            return False
        
        # Create task
        task_data = {
            "title": "API Test Task",
            "description": "A task created for API testing",
            "team": self.test_data['team_id'],
            "priority": "medium",
            "status": "todo"
        }
        
        response = self.make_request('POST', '/tasks/', task_data)
        if response and response.status_code == 201:
            self.log("✓ Create task successful")
            self.test_data['task_id'] = response.json()['id']
            return True
        else:
            self.log("✗ Create task failed")
            return False
    
    def test_utility_endpoints(self):
        """Test utility endpoints"""
        self.log("Testing utility endpoints...")
        
        endpoints = [
            '/stats/',
            '/recommendations/',
            '/activity/',
            '/skills/',
            '/skills/trending/',
            '/matching/preferences/',
            '/matching/find-teammates/'
        ]
        
        success_count = 0
        for endpoint in endpoints:
            response = self.make_request('GET', endpoint)
            if response and response.status_code == 200:
                self.log(f"✓ {endpoint} successful")
                success_count += 1
            else:
                self.log(f"✗ {endpoint} failed")
        
        return success_count == len(endpoints)
    
    def run_all_tests(self):
        """Run all API tests"""
        self.log("Starting comprehensive API tests for HackMate backend")
        self.log("=" * 60)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Profile Management", self.test_profile_management),
            ("Hackathon Operations", self.test_hackathon_operations),
            ("Team Operations", self.test_team_operations),
            ("Task Operations", self.test_task_operations),
            ("Utility Endpoints", self.test_utility_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
            else:
                self.log(f"Test '{test_name}' failed", "ERROR")
        
        self.log("\n" + "=" * 60)
        self.log(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! HackMate API is working correctly.", "SUCCESS")
            return True
        else:
            self.log(f"❌ {total - passed} tests failed. Please check the issues above.", "ERROR")
            return False


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
