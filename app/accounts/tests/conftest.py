import pytest
from accounts.models import User


@pytest.fixture
def trainee_profile(preferable_country, user):
    return user.trainee_profile


@pytest.fixture
def user2():
    return User.objects.create_user(
        first_name="user2",
        last_name="user2",
        email="user2@user.com",
        password="password",
    )
