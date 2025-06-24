from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='user_register'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/<str:user__username>/', views.UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('stats/', views.user_stats, name='user_stats'),
    path('recommendations/', views.user_recommendations, name='user_recommendations'),
    path('activity/', views.user_activity, name='user_activity'),
    path('search/users/', views.search_users, name='search_users'),
    
    # Skills endpoints
    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('skills/trending/', views.trending_skills, name='trending_skills'),
    
    # Hackathon endpoints
    path('hackathons/', views.HackathonListView.as_view(), name='hackathon_list'),
    path('hackathons/<int:pk>/', views.HackathonDetailView.as_view(), name='hackathon_detail'),
    path('hackathons/<int:hackathon_id>/analytics/', views.hackathon_analytics, name='hackathon_analytics'),
    
    # Team endpoints
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:team_id>/join/', views.join_team, name='join_team'),
    path('teams/<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('teams/<int:team_id>/invite/', views.invite_to_team, name='invite_to_team'),
    path('teams/<int:team_id>/dashboard/', views.team_dashboard, name='team_dashboard'),
    path('teams/<int:team_id>/health/', views.team_health, name='team_health'),
    path('teams/<int:team_id>/transfer-leadership/', views.transfer_leadership, name='transfer_leadership'),

    # Team invitation endpoints
    path('invitations/', views.my_invitations, name='my_invitations'),
    path('invitations/<int:invitation_id>/respond/', views.respond_to_invitation, name='respond_to_invitation'),
    
    # Task endpoints
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/comments/', views.TaskCommentListView.as_view(), name='task_comment_list'),
    path('tasks/<int:task_id>/assign/', views.assign_task, name='assign_task'),
    
    # Matching system endpoints
    path('matching/preferences/', views.MatchingPreferenceView.as_view(), name='matching_preferences'),
    path('matching/find-teammates/', views.find_teammates, name='find_teammates'),

    # Health check
    path('health/', views.health_check, name='health_check'),
]
