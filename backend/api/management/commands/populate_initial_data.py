from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from api.models import Skill, Hackathon, UserProfile


class Command(BaseCommand):
    help = 'Populate initial data for HackMate'

    def handle(self, *args, **options):
        self.stdout.write('Populating initial data...')
        
        # Create skills
        skills_data = [
            ('Python', 'backend'),
            ('JavaScript', 'frontend'),
            ('React', 'frontend'),
            ('React Native', 'mobile'),
            ('Node.js', 'backend'),
            ('Django', 'backend'),
            ('Flask', 'backend'),
            ('Vue.js', 'frontend'),
            ('Angular', 'frontend'),
            ('Swift', 'mobile'),
            ('Kotlin', 'mobile'),
            ('Java', 'backend'),
            ('C++', 'backend'),
            ('Go', 'backend'),
            ('Rust', 'backend'),
            ('PHP', 'backend'),
            ('Ruby', 'backend'),
            ('HTML/CSS', 'frontend'),
            ('TypeScript', 'frontend'),
            ('Figma', 'design'),
            ('Adobe XD', 'design'),
            ('Sketch', 'design'),
            ('UI/UX Design', 'design'),
            ('Graphic Design', 'design'),
            ('Machine Learning', 'ai_ml'),
            ('Deep Learning', 'ai_ml'),
            ('TensorFlow', 'ai_ml'),
            ('PyTorch', 'ai_ml'),
            ('Data Analysis', 'data'),
            ('SQL', 'data'),
            ('MongoDB', 'data'),
            ('PostgreSQL', 'data'),
            ('MySQL', 'data'),
            ('Redis', 'data'),
            ('Docker', 'devops'),
            ('Kubernetes', 'devops'),
            ('AWS', 'devops'),
            ('Azure', 'devops'),
            ('GCP', 'devops'),
            ('Git', 'other'),
            ('Blockchain', 'blockchain'),
            ('Solidity', 'blockchain'),
            ('Unity', 'game_dev'),
            ('Unreal Engine', 'game_dev'),
        ]
        
        for skill_name, category in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category}
            )
            if created:
                self.stdout.write(f'Created skill: {skill_name}')
        
        # Create sample hackathons
        hackathons_data = [
            {
                'title': 'AI for Good Hackathon 2024',
                'description': 'Build AI solutions that make a positive impact on society.',
                'short_description': 'AI solutions for social good',
                'location_type': 'hybrid',
                'location_details': 'San Francisco, CA + Remote',
                'start_date': timezone.now() + timedelta(days=30),
                'end_date': timezone.now() + timedelta(days=32),
                'registration_deadline': timezone.now() + timedelta(days=25),
                'organizer': 'TechForGood Foundation',
                'themes': ['AI', 'Social Impact', 'Healthcare', 'Education'],
                'required_skills': ['Python', 'Machine Learning', 'TensorFlow'],
                'prize_pool': '$50,000',
            },
            {
                'title': 'Mobile App Innovation Challenge',
                'description': 'Create innovative mobile applications that solve real-world problems.',
                'short_description': 'Innovative mobile app development',
                'location_type': 'remote',
                'location_details': 'Online via Discord',
                'start_date': timezone.now() + timedelta(days=45),
                'end_date': timezone.now() + timedelta(days=47),
                'registration_deadline': timezone.now() + timedelta(days=40),
                'organizer': 'Mobile Dev Community',
                'themes': ['Mobile', 'Innovation', 'User Experience'],
                'required_skills': ['React Native', 'Swift', 'Kotlin', 'UI/UX Design'],
                'prize_pool': '$25,000',
            },
            {
                'title': 'Blockchain & Web3 Hackathon',
                'description': 'Build the future of decentralized applications and Web3.',
                'short_description': 'Decentralized apps and Web3 solutions',
                'location_type': 'onsite',
                'location_details': 'Austin, TX',
                'start_date': timezone.now() + timedelta(days=60),
                'end_date': timezone.now() + timedelta(days=62),
                'registration_deadline': timezone.now() + timedelta(days=55),
                'organizer': 'Crypto Innovators',
                'themes': ['Blockchain', 'DeFi', 'NFTs', 'Smart Contracts'],
                'required_skills': ['Solidity', 'JavaScript', 'Web3', 'Blockchain'],
                'prize_pool': '$100,000',
            }
        ]
        
        # Get admin user to assign as creator
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@hackmate.com',
                password='admin123'
            )
        
        # Create admin profile if it doesn't exist
        UserProfile.objects.get_or_create(user=admin_user)
        
        for hackathon_data in hackathons_data:
            hackathon, created = Hackathon.objects.get_or_create(
                title=hackathon_data['title'],
                defaults={**hackathon_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(f'Created hackathon: {hackathon_data["title"]}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated initial data!')
        )
