import pytest
from accounts.models import Country, Department, User
from django.conf import settings
from internship.models import Direction
from rest_framework.test import APIClient


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


@pytest.fixture
def direction():
    return Direction.objects.create(name="Test direction")


@pytest.fixture
def user_data():
    return {
        "username": "user@user.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
        "role": User.Role.CANDIDATE,
    }


@pytest.fixture
def create_user(user_data):
    def _create_user(**kwargs):
        data = user_data.copy()
        data.update(kwargs)
        return User.objects.create_user(**data)

    return _create_user


@pytest.fixture
def candidate(create_user):
    return create_user()


@pytest.fixture
def trainee(create_user):
    return create_user(role=User.Role.TRAINEE, username="trainee@user.com")


@pytest.fixture
def mentor(create_user, department):
    return create_user(
        role=User.Role.MENTOR, username="mentor@user.com", department=department
    )


@pytest.fixture
def curator(create_user):
    return create_user(role=User.Role.CURATOR, username="curator@user.com")


@pytest.fixture
def personnel(create_user, department):
    return create_user(
        role=User.Role.PERSONNEL, username="personnel@user.com", department=department
    )


@pytest.fixture
def user(trainee):
    return trainee


@pytest.fixture
def anon_api_client():
    return APIClient()


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def candidate_client(candidate):
    client = APIClient()
    client.force_authenticate(candidate)
    return client


@pytest.fixture
def mentor_client(mentor):
    client = APIClient()
    client.force_authenticate(mentor)
    return client


@pytest.fixture
def curator_client(curator):
    client = APIClient()
    client.force_authenticate(curator)
    return client


@pytest.fixture
def personnel_client(personnel):
    client = APIClient()
    client.force_authenticate(personnel)
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
def trainee_profile(preferable_country, trainee):
    profile = trainee.trainee_profile
    profile.citizenship = preferable_country
    profile.save()
    return profile
