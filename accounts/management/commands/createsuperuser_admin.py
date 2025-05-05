from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser with user_type set to admin'

    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username', default=None,
                            help='Specifies the username for the superuser.')
        parser.add_argument('--email', dest='email', default=None,
                            help='Specifies the email address for the superuser.')
        parser.add_argument('--password', dest='password', default=None,
                            help='Specifies the password for the superuser.')
        parser.add_argument('--first_name', dest='first_name', default='Admin',
                            help='Specifies the first name for the superuser.')
        parser.add_argument('--last_name', dest='last_name', default='User',
                            help='Specifies the last name for the superuser.')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if not username:
            username = input("Username: ")
        if not email:
            email = input("Email address: ")
        if not password:
            from getpass import getpass
            password = getpass("Password: ")
            password2 = getpass("Password (again): ")
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='admin'  # Set user_type to admin
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully with user_type set to admin'))
        except IntegrityError as e:
            self.stderr.write(f"Error: {e}")
            self.stdout.write("Trying to update existing superuser...")
            try:
                user = User.objects.get(username=username)
                user.is_staff = True
                user.is_superuser = True
                user.user_type = 'admin'
                if password:
                    user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Superuser {username} updated successfully with user_type set to admin'))
            except User.DoesNotExist:
                self.stderr.write("Error: User does not exist.")
