from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserProfile, Skill, Hackathon, Team, TeamMembership, 
    TeamInvitation, Task, TaskComment, MatchingPreference
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""
    
    class Meta:
        model = Skill
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = UserProfile
        exclude = ('user', 'created_at', 'updated_at')


class HackathonSerializer(serializers.ModelSerializer):
    """Hackathon serializer"""
    
    created_by = UserSerializer(read_only=True)
    is_registration_open = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Hackathon
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class HackathonCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating hackathons"""
    
    class Meta:
        model = Hackathon
        exclude = ('created_by', 'created_at', 'updated_at')


class TeamMembershipSerializer(serializers.ModelSerializer):
    """Team membership serializer"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = '__all__'
        read_only_fields = ('joined_at', 'updated_at')


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer"""
    
    leader = UserSerializer(read_only=True)
    hackathon = HackathonSerializer(read_only=True)
    memberships = TeamMembershipSerializer(source='teammembership_set', many=True, read_only=True)
    current_size = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('leader', 'created_at', 'updated_at')


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating teams"""
    
    class Meta:
        model = Team
        exclude = ('leader', 'created_at', 'updated_at')


class TeamInvitationSerializer(serializers.ModelSerializer):
    """Team invitation serializer"""
    
    team = TeamSerializer(read_only=True)
    invited_user = UserSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamInvitation
        fields = '__all__'
        read_only_fields = ('invited_by', 'created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer"""
    
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'completed_at')


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    class Meta:
        model = Task
        exclude = ('created_by', 'created_at', 'updated_at', 'completed_at')


class TaskCommentSerializer(serializers.ModelSerializer):
    """Task comment serializer"""
    
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')


class MatchingPreferenceSerializer(serializers.ModelSerializer):
    """Matching preference serializer"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MatchingPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
