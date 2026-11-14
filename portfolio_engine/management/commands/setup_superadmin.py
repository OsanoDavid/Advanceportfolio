import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from portfolio_engine.models import NetworkRegistryTicket


class Command(BaseCommand):
    help = "Initializes or updates the Core Node super admin accounts for both Django Admin and the frontend portal."

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Superuser username')
        parser.add_argument('--email', type=str, help='Superuser email')
        parser.add_argument('--password', type=str, help='Superuser password')

    def handle(self, *args, **options):
        username = (
            options.get('username')
            or os.environ.get('DJANGO_SUPERUSER_USERNAME')
            or 'OsanoDavid'
        ).strip()

        email = (
            options.get('email')
            or os.environ.get('DJANGO_SUPERUSER_EMAIL')
            or 'osanodavid09@gmail.com'
        ).strip()

        password = (
            options.get('password')
            or os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            or '@OsanoAdmin2026!'
        )

        # 1. Setup Django User for /admin/
        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        # 2. Setup NetworkRegistryTicket for frontend /login/ and /dashboard/
        ticket, t_created = NetworkRegistryTicket.objects.get_or_create(username=username)
        ticket.full_identity = "Odiwuor David Osano"
        ticket.secure_email = email
        ticket.associated_organization = "Core Node Software Engineering Lab"
        ticket.specialization = "Full-Stack Developer"
        ticket.phone_number = "+254791209899"
        ticket.github_link = "https://github.com/OsanoDavid"
        ticket.collaboration_scope = "Lead Architect & Full-Stack Deployment Operations."
        ticket.password = make_password(password)
        ticket.is_superadmin = True
        ticket.save()

        # 3. Also ensure 'admin' alias exists with the same credentials
        if username.lower() != 'admin':
            admin_user, _ = User.objects.get_or_create(username='admin')
            admin_user.email = email
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(password)
            admin_user.save()

            admin_ticket, _ = NetworkRegistryTicket.objects.get_or_create(username='admin')
            admin_ticket.full_identity = "Odiwuor David Osano (Admin)"
            admin_ticket.secure_email = email
            admin_ticket.associated_organization = "Core Node Software Engineering Lab"
            admin_ticket.specialization = "Full-Stack Developer"
            admin_ticket.phone_number = "+254791209899"
            admin_ticket.github_link = "https://github.com/OsanoDavid"
            admin_ticket.password = make_password(password)
            admin_ticket.is_superadmin = True
            admin_ticket.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"âœ… SUPER ADMIN ACTIVE: '{username}' (and 'admin') configured with full root privileges.\n"
                f"   Login URLs: /admin/ and /login/\n"
                f"   Email: {email}"
            )
        )
