from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Echoverse.models import Profile

class Command(BaseCommand):
    help = 'Creates profiles for users who don\'t have one'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Profile created for user {user.username}'))
            else:
                self.stdout.write(f'User {user.username} already has a profile.')
