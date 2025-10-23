from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create default superuser for development'

    def handle(self, *args, **options):
        username = 'sa'
        email = 'admin@wheelerskeeper.com'
        password = 'superadminpass123'

        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Superuser "{username}" created successfully!\n'
                        f'Username: {username}\n'
                        f'Password: {password}\n'
                        f'⚠️  IMPORTANT: Please change the password on first login for security!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Superuser "{username}" already exists.')
                )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser "{username}"')
            )