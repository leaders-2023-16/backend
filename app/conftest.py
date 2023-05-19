import pytest
from accounts.models import Country, Department, User
from django.conf import settings
from rest_framework.test import APIClient


@pytest.fixture
def anon_api_client():
    return APIClient()


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def candidate_client(user):
    user.role = User.Role.CANDIDATE
    user.save()
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def curator_client(user):
    user.role = User.Role.CURATOR
    user.save()
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
    return User.objects.create_user(
        username="user@user.com",
        password="password",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture(autouse=True)
def preferable_country():
    return Country.objects.create(
        id=settings.PREFERABLE_CITIZENSHIP_ID, name="Preferable country"
    )


@pytest.fixture(autouse=True)
def non_preferable_country():
    return Country.objects.create(
        id=settings.PREFERABLE_CITIZENSHIP_ID + 1, name="Non preferable country"
    )


@pytest.fixture(autouse=True)
def department():
    return Department.objects.create(name="Department 1")


@pytest.fixture(autouse=True)
def department2():
    return Department.objects.create(name="Department 2")
