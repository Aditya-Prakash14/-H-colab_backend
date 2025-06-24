from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserProfile, Skill, Hackathon, Team, TeamMembership,
    TeamInvitation, Task, TaskComment, MatchingPreference
)
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer,
    UserSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    SkillSerializer, HackathonSerializer, HackathonCreateSerializer,
    TeamSerializer, TeamCreateSerializer, TeamMembershipSerializer,
    TeamInvitationSerializer, TaskSerializer, TaskCreateSerializer,
    TaskCommentSerializer, MatchingPreferenceSerializer
)
from .utils import (
    get_user_recommendations, calculate_team_health_score,
    get_trending_skills, get_hackathon_analytics, get_user_activity_summary
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view"""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view for authenticated user"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer


class UserProfileDetailView(generics.RetrieveAPIView):
    """Public user profile view"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__username'


class SkillListView(generics.ListCreateAPIView):
    """Skills list and create view"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['name', 'category', 'created_at']


class HackathonListView(generics.ListCreateAPIView):
    """Hackathons list and create view"""
    queryset = Hackathon.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'organizer']
    ordering_fields = ['start_date', 'created_at', 'title']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HackathonCreateSerializer
        return HackathonSerializer

    def get_queryset(self):
        queryset = Hackathon.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by location type
        location_type = self.request.query_params.get('location_type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HackathonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Hackathon detail view"""
    queryset = Hackathon.objects.all()
    serializer_class = HackathonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class TeamListView(generics.ListCreateAPIView):
    """Teams list and create view"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeamCreateSerializer
        return TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.all()

        # Filter by hackathon
        hackathon_id = self.request.query_params.get('hackathon')
        if hackathon_id:
            queryset = queryset.filter(hackathon_id=hackathon_id)

        # Filter by recruiting status
        is_recruiting = self.request.query_params.get('is_recruiting')
        if is_recruiting is not None:
            queryset = queryset.filter(is_recruiting=is_recruiting.lower() == 'true')

        # Filter teams user is member of
        my_teams = self.request.query_params.get('my_teams')
        if my_teams and my_teams.lower() == 'true':
            queryset = queryset.filter(members=self.request.user)

        return queryset

    def perform_create(self, serializer):
        team = serializer.save(leader=self.request.user)
        # Add leader as team member
        TeamMembership.objects.create(
            team=team,
            user=self.request.user,
            role='leader',
            status='accepted'
        )


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Team detail view"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_team(request, team_id):
    """Join a team"""
    team = get_object_or_404(Team, id=team_id)

    if team.is_full:
        return Response(
            {'error': 'Team is full'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if TeamMembership.objects.filter(team=team, user=request.user).exists():
        return Response(
            {'error': 'Already a member of this team'},
            status=status.HTTP_400_BAD_REQUEST
        )

    role = request.data.get('role', 'developer')
    membership = TeamMembership.objects.create(
        team=team,
        user=request.user,
        role=role,
        status='pending'
    )

    serializer = TeamMembershipSerializer(membership)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_team(request, team_id):
    """Leave a team"""
    team = get_object_or_404(Team, id=team_id)

    try:
        membership = TeamMembership.objects.get(team=team, user=request.user)
        if membership.role == 'leader':
            return Response(
                {'error': 'Team leader cannot leave. Transfer leadership first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        membership.status = 'left'
        membership.save()
        return Response({'message': 'Left team successfully'})
    except TeamMembership.DoesNotExist:
        return Response(
            {'error': 'Not a member of this team'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_to_team(request, team_id):
    """Invite user to team"""
    team = get_object_or_404(Team, id=team_id)

    # Check if user is team leader or member
    if not TeamMembership.objects.filter(
        team=team,
        user=request.user,
        status='accepted'
    ).exists():
        return Response(
            {'error': 'Only team members can send invitations'},
            status=status.HTTP_403_FORBIDDEN
        )

    username = request.data.get('username')
    role = request.data.get('role', 'developer')
    message = request.data.get('message', '')

    try:
        invited_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if already invited or member
    if TeamInvitation.objects.filter(
        team=team,
        invited_user=invited_user,
        status='pending'
    ).exists():
        return Response(
            {'error': 'User already invited'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if TeamMembership.objects.filter(team=team, user=invited_user).exists():
        return Response(
            {'error': 'User already a member'},
            status=status.HTTP_400_BAD_REQUEST
        )

    invitation = TeamInvitation.objects.create(
        team=team,
        invited_user=invited_user,
        invited_by=request.user,
        role=role,
        message=message,
        expires_at=timezone.now() + timedelta(days=7)
    )

    serializer = TeamInvitationSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskListView(generics.ListCreateAPIView):
    """Tasks list and create view"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()

        # Filter by team
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to__username=assigned_to)

        # Filter by status
        task_status = self.request.query_params.get('status')
        if task_status:
            queryset = queryset.filter(status=task_status)

        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter user's tasks
        my_tasks = self.request.query_params.get('my_tasks')
        if my_tasks and my_tasks.lower() == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Task detail view"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskCommentListView(generics.ListCreateAPIView):
    """Task comments list and create view"""
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)


class MatchingPreferenceView(generics.RetrieveUpdateAPIView):
    """Matching preferences view"""
    serializer_class = MatchingPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        preference, created = MatchingPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def find_teammates(request):
    """Find potential teammates based on preferences and skills"""
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    # Get user's matching preferences
    try:
        preferences = user.matching_preferences
    except MatchingPreference.DoesNotExist:
        preferences = None

    # Base queryset - exclude current user
    potential_teammates = UserProfile.objects.exclude(user=user).filter(
        is_available=True
    )

    # Filter by skills if user has preferences
    if preferences and preferences.preferred_skills:
        skill_filter = Q()
        for skill in preferences.preferred_skills:
            skill_filter |= Q(skills__icontains=skill)
        potential_teammates = potential_teammates.filter(skill_filter)

    # Filter by experience level
    if preferences and preferences.experience_level_preference:
        potential_teammates = potential_teammates.filter(
            experience_level__in=preferences.experience_level_preference
        )

    # Filter by location preference
    if preferences and preferences.location_preference != 'any':
        if preferences.location_preference == 'same_timezone':
            potential_teammates = potential_teammates.filter(
                timezone=user_profile.timezone
            )
        elif preferences.location_preference == 'same_country':
            # Simple location matching - in real app, use proper geo data
            user_location_parts = user_profile.location.split(',')
            if len(user_location_parts) >= 2:
                country = user_location_parts[-1].strip()
                potential_teammates = potential_teammates.filter(
                    location__icontains=country
                )

    # Calculate compatibility scores (simple algorithm)
    teammates_with_scores = []
    for teammate in potential_teammates[:50]:  # Limit for performance
        score = calculate_compatibility_score(user_profile, teammate, preferences)
        teammates_with_scores.append({
            'profile': teammate,
            'compatibility_score': score
        })

    # Sort by compatibility score
    teammates_with_scores.sort(key=lambda x: x['compatibility_score'], reverse=True)

    # Serialize results
    results = []
    for item in teammates_with_scores[:20]:  # Return top 20
        profile_data = UserProfileSerializer(item['profile']).data
        profile_data['compatibility_score'] = item['compatibility_score']
        results.append(profile_data)

    return Response(results)


def calculate_compatibility_score(user_profile, teammate_profile, preferences):
    """Calculate compatibility score between two users"""
    score = 0

    # Skill matching (40% weight)
    if user_profile.skills and teammate_profile.skills:
        common_skills = set(user_profile.skills) & set(teammate_profile.skills)
        skill_score = len(common_skills) / max(len(user_profile.skills), 1) * 40
        score += skill_score

    # Experience level compatibility (20% weight)
    experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
    user_exp_idx = experience_levels.index(user_profile.experience_level)
    teammate_exp_idx = experience_levels.index(teammate_profile.experience_level)
    exp_diff = abs(user_exp_idx - teammate_exp_idx)
    exp_score = max(0, (3 - exp_diff) / 3) * 20
    score += exp_score

    # Role compatibility (20% weight)
    if (user_profile.preferred_roles and teammate_profile.preferred_roles):
        common_roles = set(user_profile.preferred_roles) & set(teammate_profile.preferred_roles)
        # Prefer complementary roles rather than same roles
        if common_roles:
            role_score = 10  # Some overlap is good
        else:
            role_score = 20  # Different roles are better for team diversity
        score += role_score

    # Location/timezone compatibility (20% weight)
    if user_profile.timezone and teammate_profile.timezone:
        if user_profile.timezone == teammate_profile.timezone:
            score += 20
        else:
            score += 10  # Different timezones can still work

    return min(score, 100)  # Cap at 100


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics"""
    user = request.user

    stats = {
        'teams_count': Team.objects.filter(members=user).count(),
        'led_teams_count': Team.objects.filter(leader=user).count(),
        'tasks_assigned': Task.objects.filter(assigned_to=user).count(),
        'tasks_completed': Task.objects.filter(
            assigned_to=user,
            status='done'
        ).count(),
        'hackathons_participated': Hackathon.objects.filter(
            teams__members=user
        ).distinct().count(),
    }

    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_invitation(request, invitation_id):
    """Accept or decline team invitation"""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, invited_user=request.user)

    if invitation.is_expired:
        return Response(
            {'error': 'Invitation has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if invitation.status != 'pending':
        return Response(
            {'error': 'Invitation already responded to'},
            status=status.HTTP_400_BAD_REQUEST
        )

    action = request.data.get('action')  # 'accept' or 'decline'

    if action == 'accept':
        if invitation.team.is_full:
            return Response(
                {'error': 'Team is full'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create team membership
        TeamMembership.objects.create(
            team=invitation.team,
            user=request.user,
            role=invitation.role,
            status='accepted'
        )
        invitation.status = 'accepted'
        invitation.save()

        return Response({'message': 'Invitation accepted successfully'})

    elif action == 'decline':
        invitation.status = 'declined'
        invitation.save()
        return Response({'message': 'Invitation declined'})

    else:
        return Response(
            {'error': 'Invalid action. Use "accept" or "decline"'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_invitations(request):
    """Get user's pending invitations"""
    invitations = TeamInvitation.objects.filter(
        invited_user=request.user,
        status='pending'
    ).select_related('team', 'invited_by')

    serializer = TeamInvitationSerializer(invitations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_task(request, task_id):
    """Assign task to a team member"""
    task = get_object_or_404(Task, id=task_id)

    # Check if user is team member
    if not TeamMembership.objects.filter(
        team=task.team,
        user=request.user,
        status='accepted'
    ).exists():
        return Response(
            {'error': 'Only team members can assign tasks'},
            status=status.HTTP_403_FORBIDDEN
        )

    username = request.data.get('username')
    if not username:
        return Response(
            {'error': 'Username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        assignee = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if assignee is team member
    if not TeamMembership.objects.filter(
        team=task.team,
        user=assignee,
        status='accepted'
    ).exists():
        return Response(
            {'error': 'User is not a team member'},
            status=status.HTTP_400_BAD_REQUEST
        )

    task.assigned_to = assignee
    task.save()

    serializer = TaskSerializer(task)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_dashboard(request, team_id):
    """Get team dashboard data"""
    team = get_object_or_404(Team, id=team_id)

    # Check if user is team member
    if not TeamMembership.objects.filter(
        team=team,
        user=request.user,
        status='accepted'
    ).exists():
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get team statistics
    tasks = Task.objects.filter(team=team)
    members = TeamMembership.objects.filter(team=team, status='accepted')

    dashboard_data = {
        'team': TeamSerializer(team).data,
        'stats': {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'in_progress_tasks': tasks.filter(status='in_progress').count(),
            'overdue_tasks': sum(1 for task in tasks if task.is_overdue),
            'total_members': members.count(),
        },
        'recent_tasks': TaskSerializer(
            tasks.order_by('-created_at')[:5],
            many=True
        ).data,
        'members': TeamMembershipSerializer(members, many=True).data,
    }

    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_recommendations(request):
    """Get personalized recommendations for the user"""
    recommendations = get_user_recommendations(request.user)

    # Serialize the recommendations
    serialized_recommendations = {}

    if 'hackathons' in recommendations:
        serialized_recommendations['hackathons'] = HackathonSerializer(
            recommendations['hackathons'], many=True
        ).data

    if 'teams' in recommendations:
        serialized_recommendations['teams'] = TeamSerializer(
            recommendations['teams'], many=True
        ).data

    return Response(serialized_recommendations)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def trending_skills(request):
    """Get trending skills"""
    skills = get_trending_skills()
    return Response(skills)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def hackathon_analytics(request, hackathon_id):
    """Get analytics for a specific hackathon"""
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    analytics = get_hackathon_analytics(hackathon)
    return Response(analytics)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity(request):
    """Get user activity summary"""
    days = int(request.query_params.get('days', 30))
    activity = get_user_activity_summary(request.user, days)
    return Response(activity)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_health(request, team_id):
    """Get team health score"""
    team = get_object_or_404(Team, id=team_id)

    # Check if user is team member
    if not TeamMembership.objects.filter(
        team=team,
        user=request.user,
        status='accepted'
    ).exists():
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )

    health_score = calculate_team_health_score(team)

    return Response({
        'team_id': team_id,
        'health_score': health_score,
        'status': 'excellent' if health_score >= 80 else
                 'good' if health_score >= 60 else
                 'needs_improvement' if health_score >= 40 else 'poor'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer_leadership(request, team_id):
    """Transfer team leadership to another member"""
    team = get_object_or_404(Team, id=team_id)

    # Check if user is current leader
    if team.leader != request.user:
        return Response(
            {'error': 'Only team leader can transfer leadership'},
            status=status.HTTP_403_FORBIDDEN
        )

    new_leader_username = request.data.get('new_leader')
    if not new_leader_username:
        return Response(
            {'error': 'new_leader username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        new_leader = User.objects.get(username=new_leader_username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if new leader is team member
    try:
        new_leader_membership = TeamMembership.objects.get(
            team=team,
            user=new_leader,
            status='accepted'
        )
    except TeamMembership.DoesNotExist:
        return Response(
            {'error': 'User is not a team member'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update leadership
    old_leader_membership = TeamMembership.objects.get(
        team=team,
        user=request.user
    )

    team.leader = new_leader
    team.save()

    # Update roles
    new_leader_membership.role = 'leader'
    new_leader_membership.save()

    old_leader_membership.role = 'developer'  # Default role for ex-leader
    old_leader_membership.save()

    return Response({'message': f'Leadership transferred to {new_leader_username}'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    """Search for users by username, name, or skills"""
    query = request.query_params.get('q', '')
    if not query:
        return Response({'error': 'Query parameter "q" is required'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Search in username, first_name, last_name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]

    # Also search by skills
    profiles_by_skills = UserProfile.objects.filter(
        skills__icontains=query
    ).exclude(user=request.user)[:20]

    # Combine results
    user_ids = set(user.id for user in users)
    for profile in profiles_by_skills:
        if profile.user.id not in user_ids:
            users = list(users) + [profile.user]
            user_ids.add(profile.user.id)

    # Serialize results
    results = []
    for user in users[:20]:  # Limit to 20 results
        user_data = UserSerializer(user).data
        try:
            profile = user.profile
            user_data['skills'] = profile.skills
            user_data['experience_level'] = profile.experience_level
        except UserProfile.DoesNotExist:
            pass
        results.append(user_data)

    return Response(results)
