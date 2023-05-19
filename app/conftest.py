import pytest
from accounts.models import User
from rest_framework.test import APIClient


@pytest.fixture
def anon_api_client():
    return APIClient()


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture(
    params=[
        pytest.param("anon"),
        pytest.param("auth"),
    ]
)
def generic_api_client(request, anon_api_client, api_client):
    if request.param == "anon":
        return anon_api_client
    return api_client


@pytest.fixture
def user():
    return User.objects.create_user(username="user@user.com", password="password")
