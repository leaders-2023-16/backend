import pytest
from accounts.models import User


@pytest.fixture
def user2():
    return User.objects.create_user(
        username="user2@user.com",
        password="password",
        first_name="Johny",
        last_name="Doel",
    )
