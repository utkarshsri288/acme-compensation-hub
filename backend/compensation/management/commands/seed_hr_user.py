import os
from getpass import getpass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from compensation.roles import ADMIN
from compensation.passwords import password_validation_errors

class Command(BaseCommand):
    help = "Create the demo administrator if it does not already exist."
    def handle(self, *args, **options):
        User = get_user_model()
        username = "acme_admin"
        email = "hr.manager@acme.example"
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Demo HR account already exists; credentials and role unchanged: {username}"))
            return

        password = os.getenv("DJANGO_DEMO_ADMIN_PASSWORD")
        if not password:
            if settings.DEBUG:
                password = "AcmeHR2026!"
            else:
                password = getpass("Choose a unique app admin password: ")
                confirmation = getpass("Confirm app admin password: ")
                if password != confirmation:
                    raise CommandError("Passwords did not match; no account was created.")
        if not password:
            raise CommandError("An app admin password is required.")
        errors = password_validation_errors(password, username)
        if errors:
            raise CommandError("Admin password must contain " + ", ".join(errors) + ".")
        user = User(username=username, email=email, first_name="Alex", last_name="Reed", is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        user.groups.add(Group.objects.get(name=ADMIN))
        self.stdout.write(self.style.SUCCESS(f"Demo admin account ready: {username}"))
