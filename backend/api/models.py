from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile with additional fields for HackMate"""

    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Tell others about yourself")
    skills = models.JSONField(default=list, help_text="List of technical skills")
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default='beginner'
    )
    github_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    linkedin_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    portfolio_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    location = models.CharField(max_length=100, blank=True, help_text="City, Country")
    timezone = models.CharField(max_length=50, blank=True, help_text="User's timezone")
    availability = models.JSONField(
        default=dict,
        help_text="Availability preferences (days, hours, etc.)"
    )
    preferred_roles = models.JSONField(
        default=list,
        help_text="Preferred team roles (Developer, Designer, PM, etc.)"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether user is available for new teams"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Skill(models.Model):
    """Predefined skills that users can select from"""

    SKILL_CATEGORIES = [
        ('frontend', 'Frontend Development'),
        ('backend', 'Backend Development'),
        ('mobile', 'Mobile Development'),
        ('design', 'Design'),
        ('data', 'Data Science/Analytics'),
        ('devops', 'DevOps/Infrastructure'),
        ('ai_ml', 'AI/Machine Learning'),
        ('blockchain', 'Blockchain'),
        ('game_dev', 'Game Development'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']


class Hackathon(models.Model):
    """Hackathon event model"""

    LOCATION_TYPES = [
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300,
        help_text="Brief description for listings"
    )
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPES)
    location_details = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specific location or platform details"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    max_team_size = models.PositiveIntegerField(default=4)
    min_team_size = models.PositiveIntegerField(default=1)
    prize_pool = models.CharField(max_length=100, blank=True)
    themes = models.JSONField(
        default=list,
        help_text="List of hackathon themes/tracks"
    )
    required_skills = models.JSONField(
        default=list,
        help_text="Recommended skills for participants"
    )
    website_url = models.URLField(blank=True, null=True)
    registration_url = models.URLField(blank=True, null=True)
    organizer = models.CharField(max_length=200)
    organizer_contact = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField(default=False)
    banner_image = models.ImageField(
        upload_to='hackathon_banners/',
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_hackathons'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_registration_open(self):
        return timezone.now() < self.registration_deadline

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    class Meta:
        ordering = ['-start_date']


class Team(models.Model):
    """Team model for hackathon participation"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='led_teams'
    )
    members = models.ManyToManyField(
        User,
        through='TeamMembership',
        related_name='teams'
    )
    is_recruiting = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=4)
    required_skills = models.JSONField(
        default=list,
        help_text="Skills the team is looking for"
    )
    project_idea = models.TextField(
        blank=True,
        help_text="Initial project idea or description"
    )
    github_repo = models.URLField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.hackathon.title}"

    @property
    def current_size(self):
        return self.members.count()

    @property
    def is_full(self):
        return self.current_size >= self.max_members

    class Meta:
        unique_together = ['name', 'hackathon']
        ordering = ['-created_at']


class TeamMembership(models.Model):
    """Through model for team membership with roles"""

    ROLE_CHOICES = [
        ('leader', 'Team Leader'),
        ('developer', 'Developer'),
        ('frontend_dev', 'Frontend Developer'),
        ('backend_dev', 'Backend Developer'),
        ('mobile_dev', 'Mobile Developer'),
        ('designer', 'UI/UX Designer'),
        ('pm', 'Project Manager'),
        ('data_scientist', 'Data Scientist'),
        ('devops', 'DevOps Engineer'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('left', 'Left Team'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"

    class Meta:
        unique_together = ['team', 'user']
        ordering = ['-joined_at']


class TeamInvitation(models.Model):
    """Model for team invitations"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_invitations'
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    role = models.CharField(max_length=20, choices=TeamMembership.ROLE_CHOICES)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invitation to {self.invited_user.username} for {self.team.name}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        unique_together = ['team', 'invited_user']
        ordering = ['-created_at']


class Task(models.Model):
    """Task model for team task management"""

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated hours to complete"
    )
    tags = models.JSONField(default=list, help_text="Task tags for organization")
    dependencies = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.team.name}"

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'done':
            return timezone.now() > self.due_date
        return False

    def save(self, *args, **kwargs):
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']


class TaskComment(models.Model):
    """Comments on tasks for team collaboration"""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

    class Meta:
        ordering = ['created_at']


class MatchingPreference(models.Model):
    """User preferences for teammate matching"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='matching_preferences'
    )
    preferred_team_size = models.PositiveIntegerField(default=4)
    preferred_roles = models.JSONField(
        default=list,
        help_text="Preferred roles to work with"
    )
    preferred_skills = models.JSONField(
        default=list,
        help_text="Skills looking for in teammates"
    )
    experience_level_preference = models.JSONField(
        default=list,
        help_text="Preferred experience levels of teammates"
    )
    location_preference = models.CharField(
        max_length=20,
        choices=[
            ('any', 'Any'),
            ('same_timezone', 'Same Timezone'),
            ('same_country', 'Same Country'),
            ('same_city', 'Same City'),
        ],
        default='any'
    )
    communication_style = models.JSONField(
        default=list,
        help_text="Preferred communication methods"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Matching Preferences"
