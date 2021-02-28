"""
    Create or update Django super user with a unusable password

    A "unusable password" because it's not needed while auth via SSOwat ;)

    Can be called e.g.:
        ./manage.py create_superuser --username="bar" --email="foo@bar.tld"
"""


import sys

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Create or update Django super user with a unusable password (auth via SSOwat)'

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            action="store",
            required=True,
        )
        parser.add_argument(
            "--email",
            action="store",
            default=None,
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user:
            self.stderr.write(f'Update existing user "{user}" and set his password.')
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            if email:
                user.email = email
        else:
            print(f'Create new super user "{username}"', file=sys.stderr)
            user = User.objects.create_superuser(username=username, email=email, password=None)

        user.set_unusable_password()
        user.save()
