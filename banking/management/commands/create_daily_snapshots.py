from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from banking.views import create_daily_snapshot

class Command(BaseCommand):
    help = 'Creates daily account snapshots for all users'

    def handle(self, *args, **options):
        User = get_user_model()
        for user in User.objects.all():
            create_daily_snapshot(user)
        self.stdout.write('Successfully created daily snapshots')