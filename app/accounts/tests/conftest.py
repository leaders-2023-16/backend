import pytest
from accounts.models import Country, User
from django.conf import settings


@pytest.fixture
def country():
    return Country.objects.create(
        id=settings.PREFERABLE_CITIZENSHIP_ID, name="Российская федерация"
    )


@pytest.fixture
def country2():
    return Country.objects.create(id=2, name="Country B")


@pytest.fixture
def trainee_profile(country, user):
    return user.trainee_profile


@pytest.fixture
def user2():
    return User.objects.create_user(username="user2@user.com", password="password")
