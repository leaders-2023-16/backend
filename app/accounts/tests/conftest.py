import pytest
from accounts.models import User


@pytest.fixture
def trainee_profile(preferable_country, user):
    profile = user.trainee_profile
    profile.citizenship = preferable_country
    profile.save()
    return profile


@pytest.fixture
def user2():
    return User.objects.create_user(
        username="user2@user.com",
        password="password",
        first_name="Johny",
        last_name="Doel",
    )
