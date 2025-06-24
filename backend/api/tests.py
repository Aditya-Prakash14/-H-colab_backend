from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, Skill, Hackathon, Team, Task


class AuthenticationTestCase(APITestCase):
    """Test authentication endpoints"""

    def test_user_registration(self):
        """Test user registration"""
        url = reverse('user_register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='testuser').exists())

    def test_user_login(self):
        """Test user login"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserProfileTestCase(APITestCase):
    """Test user profile endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.profile = UserProfile.objects.create(user=self.user)

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_user_profile(self):
        """Test getting user profile"""
        url = reverse('user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_update_user_profile(self):
        """Test updating user profile"""
        url = reverse('user_profile')
        data = {
            'bio': 'Updated bio',
            'skills': ['Python', 'Django'],
            'experience_level': 'intermediate'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.skills, ['Python', 'Django'])


class HackathonTestCase(APITestCase):
    """Test hackathon endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_hackathons(self):
        """Test listing hackathons"""
        url = reverse('hackathon_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_hackathon(self):
        """Test creating a hackathon"""
        url = reverse('hackathon_list')
        data = {
            'title': 'Test Hackathon',
            'description': 'A test hackathon',
            'short_description': 'Test hackathon',
            'location_type': 'remote',
            'start_date': '2024-12-01T10:00:00Z',
            'end_date': '2024-12-03T18:00:00Z',
            'registration_deadline': '2024-11-25T23:59:59Z',
            'organizer': 'Test Organizer',
            'hackathon': 1  # This should be excluded in the serializer
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Hackathon.objects.filter(title='Test Hackathon').exists())


class TeamTestCase(APITestCase):
    """Test team endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.hackathon = Hackathon.objects.create(
            title='Test Hackathon',
            description='Test description',
            short_description='Test',
            location_type='remote',
            start_date='2024-12-01T10:00:00Z',
            end_date='2024-12-03T18:00:00Z',
            registration_deadline='2024-11-25T23:59:59Z',
            organizer='Test Organizer',
            created_by=self.user
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_team(self):
        """Test creating a team"""
        url = reverse('team_list')
        data = {
            'name': 'Test Team',
            'description': 'A test team',
            'hackathon': self.hackathon.id,
            'max_members': 4
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(name='Test Team').exists())

        # Check that leader was added as member
        team = Team.objects.get(name='Test Team')
        self.assertTrue(team.teammembership_set.filter(
            user=self.user,
            role='leader'
        ).exists())


class ModelTestCase(TestCase):
    """Test model methods and properties"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

    def test_user_profile_creation(self):
        """Test user profile creation"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertTrue(profile.is_available)

    def test_skill_creation(self):
        """Test skill creation"""
        skill = Skill.objects.create(
            name='Python',
            category='backend',
            description='Python programming language'
        )
        self.assertEqual(str(skill), 'Python')

    def test_team_properties(self):
        """Test team model properties"""
        hackathon = Hackathon.objects.create(
            title='Test Hackathon',
            description='Test description',
            short_description='Test',
            location_type='remote',
            start_date='2024-12-01T10:00:00Z',
            end_date='2024-12-03T18:00:00Z',
            registration_deadline='2024-11-25T23:59:59Z',
            organizer='Test Organizer',
            created_by=self.user
        )

        team = Team.objects.create(
            name='Test Team',
            hackathon=hackathon,
            leader=self.user,
            max_members=2
        )

        self.assertEqual(team.current_size, 0)  # No members added yet
        self.assertFalse(team.is_full)
