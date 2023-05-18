from accounts.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создание пользователя по умолчанию"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username of the user")
        parser.add_argument("email", type=str, help="Email address of the user")
        parser.add_argument("password", type=str, help="Password for the user")

    def handle(self, *args, **kwargs):
        username = kwargs["username"]
        email = kwargs["email"]
        password = kwargs["password"]

        options = {"email": email}
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, password, **options)
