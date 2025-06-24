from django.contrib import admin
from .models import (
    UserProfile, Skill, Hackathon, Team, TeamMembership,
    TeamInvitation, Task, TaskComment, MatchingPreference
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_level', 'is_available', 'created_at')
    list_filter = ('experience_level', 'is_available', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'location_type', 'start_date', 'status')
    list_filter = ('location_type', 'status', 'start_date', 'is_featured')
    search_fields = ('title', 'organizer', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'hackathon', 'leader', 'current_size', 'is_recruiting')
    list_filter = ('hackathon', 'is_recruiting', 'created_at')
    search_fields = ('name', 'description', 'leader__username')
    readonly_fields = ('created_at', 'updated_at', 'current_size')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status', 'joined_at')
    search_fields = ('user__username', 'team__name')


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('invited_user', 'team', 'invited_by', 'role', 'status', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('invited_user__username', 'team__name', 'invited_by__username')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'team__name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('task__title', 'author__username', 'content')


@admin.register(MatchingPreference)
class MatchingPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_team_size', 'location_preference', 'created_at')
    list_filter = ('location_preference', 'created_at')
    search_fields = ('user__username',)
