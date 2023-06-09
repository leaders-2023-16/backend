import pytest
from accounts.models import User
from django.urls import reverse
from internship.models import Vacancy
from rest_framework import status


@pytest.mark.django_db
def test_get_list_of_users(personnel_client, mentor):
    url = reverse("users-list")
    response = personnel_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_list_of_users_unauthenticated(anon_api_client):
    url = reverse("users-list")
    response = anon_api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_list_of_users_trainee(api_client):
    url = reverse("users-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_empty_list_of_users_mentor(mentor_client, trainee):
    url = reverse("users-list")
    response = mentor_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_get_list_of_users_mentor(mentor_client, trainee, vacancy_response):
    url = reverse("users-list")
    response = mentor_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_list_of_users_curator(
    curator_client, trainee, candidate, mentor, personnel
):
    url = reverse("users-list")
    response = curator_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5

    roles = [
        User.Role.CURATOR,
        User.Role.TRAINEE,
        User.Role.CANDIDATE,
        User.Role.MENTOR,
        User.Role.PERSONNEL,
    ]
    for role in roles:
        response = curator_client.get(url, {"role": role})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
def test_get_free_mentors_forbidden(api_client, mentor):
    url = reverse("users-free-mentors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_free_mentors(personnel_client, mentor):
    url = reverse("users-free-mentors")
    response = personnel_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_free_mentors_empty(personnel_client, mentor, published_vacancy):
    url = reverse("users-free-mentors")
    response = personnel_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_get_free_mentors_closed_vacancy(personnel_client, mentor, published_vacancy):
    url = reverse("users-free-mentors")
    published_vacancy.status = Vacancy.Status.CLOSED
    published_vacancy.save()
    response = personnel_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
