"""
Utility functions for the HackMate API
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Team, Task, Hackathon


def get_user_recommendations(user):
    """Get personalized recommendations for a user"""
    user_profile = getattr(user, 'profile', None)
    if not user_profile:
        return {}
    
    recommendations = {}
    
    # Recommend hackathons based on user skills
    if user_profile.skills:
        skill_filter = Q()
        for skill in user_profile.skills:
            skill_filter |= Q(required_skills__icontains=skill)
        
        recommended_hackathons = Hackathon.objects.filter(
            skill_filter,
            status='upcoming',
            registration_deadline__gt=timezone.now()
        ).distinct()[:5]
        
        recommendations['hackathons'] = recommended_hackathons
    
    # Recommend teams looking for user's skills
    if user_profile.skills:
        skill_filter = Q()
        for skill in user_profile.skills:
            skill_filter |= Q(required_skills__icontains=skill)
        
        recommended_teams = Team.objects.filter(
            skill_filter,
            is_recruiting=True
        ).exclude(
            members=user
        ).distinct()[:5]
        
        recommendations['teams'] = recommended_teams
    
    return recommendations


def calculate_team_health_score(team):
    """Calculate a health score for a team based on various metrics"""
    score = 0
    max_score = 100
    
    # Task completion rate (40 points)
    tasks = Task.objects.filter(team=team)
    if tasks.exists():
        completed_tasks = tasks.filter(status='done').count()
        completion_rate = completed_tasks / tasks.count()
        score += completion_rate * 40
    else:
        score += 20  # Neutral score if no tasks yet
    
    # Team size optimization (20 points)
    current_size = team.current_size
    optimal_size = team.max_members * 0.8  # 80% of max is considered optimal
    if current_size >= optimal_size:
        score += 20
    else:
        score += (current_size / optimal_size) * 20
    
    # Recent activity (20 points)
    recent_activity = Task.objects.filter(
        team=team,
        updated_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    if recent_activity > 0:
        score += min(recent_activity * 5, 20)
    
    # Overdue tasks penalty (20 points)
    overdue_tasks = sum(1 for task in tasks if task.is_overdue)
    if overdue_tasks == 0:
        score += 20
    else:
        penalty = min(overdue_tasks * 5, 20)
        score += max(0, 20 - penalty)
    
    return min(score, max_score)


def get_trending_skills():
    """Get trending skills based on user profiles and team requirements"""
    # Count skills in user profiles
    user_skills = {}
    for profile in UserProfile.objects.exclude(skills=[]):
        for skill in profile.skills:
            user_skills[skill] = user_skills.get(skill, 0) + 1
    
    # Count skills in team requirements
    team_skills = {}
    for team in Team.objects.exclude(required_skills=[]):
        for skill in team.required_skills:
            team_skills[skill] = team_skills.get(skill, 0) + 1
    
    # Combine and sort
    all_skills = {}
    for skill, count in user_skills.items():
        all_skills[skill] = all_skills.get(skill, 0) + count
    
    for skill, count in team_skills.items():
        all_skills[skill] = all_skills.get(skill, 0) + count * 2  # Weight team requirements higher
    
    # Return top 10 trending skills
    trending = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{'skill': skill, 'count': count} for skill, count in trending]


def get_hackathon_analytics(hackathon):
    """Get analytics data for a hackathon"""
    teams = Team.objects.filter(hackathon=hackathon)
    
    analytics = {
        'total_teams': teams.count(),
        'total_participants': sum(team.current_size for team in teams),
        'average_team_size': teams.aggregate(
            avg_size=Count('members')
        )['avg_size'] or 0,
        'teams_recruiting': teams.filter(is_recruiting=True).count(),
        'skill_distribution': {},
        'role_distribution': {},
    }
    
    # Analyze skill distribution
    skill_counts = {}
    for team in teams:
        for skill in team.required_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    analytics['skill_distribution'] = dict(
        sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    
    # Analyze role distribution
    from .models import TeamMembership
    role_counts = TeamMembership.objects.filter(
        team__hackathon=hackathon,
        status='accepted'
    ).values('role').annotate(count=Count('role'))
    
    analytics['role_distribution'] = {
        item['role']: item['count'] for item in role_counts
    }
    
    return analytics


def send_notification(user, notification_type, data):
    """
    Placeholder for notification system
    In a real implementation, this would send push notifications,
    emails, or in-app notifications
    """
    # This would integrate with services like:
    # - Firebase Cloud Messaging for push notifications
    # - SendGrid/Mailgun for emails
    # - WebSocket for real-time notifications
    
    notification_data = {
        'user': user.id,
        'type': notification_type,
        'data': data,
        'timestamp': timezone.now().isoformat(),
    }
    
    # For now, just log the notification
    print(f"Notification for {user.username}: {notification_type} - {data}")
    
    return notification_data


def validate_team_formation(team_data, user):
    """Validate team formation rules"""
    errors = []
    
    # Check hackathon registration deadline
    hackathon = team_data.get('hackathon')
    if hackathon and not hackathon.is_registration_open:
        errors.append("Registration deadline has passed for this hackathon")
    
    # Check if user is already in a team for this hackathon
    if hackathon:
        existing_team = Team.objects.filter(
            hackathon=hackathon,
            members=user
        ).first()
        if existing_team:
            errors.append(f"You are already in team '{existing_team.name}' for this hackathon")
    
    # Validate team size
    max_members = team_data.get('max_members', 4)
    if max_members < 1 or max_members > 10:
        errors.append("Team size must be between 1 and 10 members")
    
    return errors


def get_user_activity_summary(user, days=30):
    """Get user activity summary for the past N days"""
    since_date = timezone.now() - timedelta(days=days)
    
    summary = {
        'teams_joined': Team.objects.filter(
            members=user,
            teammembership__joined_at__gte=since_date
        ).count(),
        'tasks_completed': Task.objects.filter(
            assigned_to=user,
            status='done',
            completed_at__gte=since_date
        ).count(),
        'tasks_created': Task.objects.filter(
            created_by=user,
            created_at__gte=since_date
        ).count(),
        'invitations_sent': user.sent_invitations.filter(
            created_at__gte=since_date
        ).count(),
        'invitations_received': user.team_invitations.filter(
            created_at__gte=since_date
        ).count(),
    }
    
    return summary
