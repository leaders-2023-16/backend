import pytest
from django.urls import reverse
from internship.models import TestTask, Vacancy
from rest_framework import status


@pytest.mark.django_db
def test_unauthorized_get_vacancies(anon_api_client, internship_application):
    url = reverse("vacancies-list")
    response = anon_api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_vacancies(api_client, not_published_vacancy, internship_application):
    url = reverse("vacancies-list")
    response = api_client.get(url, {"status": Vacancy.Status.PUBLISHED})
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 0

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 0

    # publish vacancy
    not_published_vacancy.status = Vacancy.Status.PUBLISHED
    not_published_vacancy.save()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 1
    assert data[0]["name"] == not_published_vacancy.name
    assert data[0]["description"] == not_published_vacancy.description
    assert data[0]["status"] == not_published_vacancy.status
    assert data[0]["direction"]["name"] == not_published_vacancy.direction.name
    assert data[0]["department"]["name"] == not_published_vacancy.department.name
    assert data[0]["owner"]["email"] == not_published_vacancy.owner.email


@pytest.mark.django_db
def test_create_vacancy(personnel_client, vacancy_data, direction, mentor, personnel):
    url = reverse("vacancies-list")
    vacancy_data = {
        **vacancy_data,
        "status": Vacancy.Status.PUBLISHED,
        "direction": direction.id,
        "mentor": mentor.id,
        "required_qualifications": ["qualification"],
        "test_task": {"title": "Test", "description": "Description", "type": "text"},
    }

    # Make a POST request to create the internship application
    response = personnel_client.post(url, vacancy_data, format="json")

    # Assert that the request was successful and the object was created
    assert response.status_code == status.HTTP_201_CREATED
    assert Vacancy.objects.count() == 1
    actual_vacancy = Vacancy.objects.get()
    assert actual_vacancy.status == Vacancy.Status.PENDING
    assert actual_vacancy.mentor == mentor
    assert actual_vacancy.required_qualifications.count() == 1
    assert actual_vacancy.required_qualifications.first().name == "qualification"
    assert actual_vacancy.direction == direction
    assert actual_vacancy.department == personnel.department
    assert TestTask.objects.count() == 1
    test_task = TestTask.objects.get()
    assert test_task.title == vacancy_data["test_task"]["title"]
    assert test_task.description == vacancy_data["test_task"]["description"]
    assert test_task.type == vacancy_data["test_task"]["type"]


@pytest.mark.django_db
def test_publish_vacancy(
    curator_client,
    curator,
    not_published_vacancy,
    direction,
    mentor,
    qualification,
    personnel,
):
    url = reverse("vacancies-detail", args=[not_published_vacancy.id])
    vacancy_data = {
        "status": Vacancy.Status.PUBLISHED,
        "required_qualifications": [],
        "test_task": {"title": "Test2", "description": "Description2", "type": "text"},
    }

    response = curator_client.patch(url, vacancy_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert Vacancy.objects.count() == 1
    actual_vacancy = Vacancy.objects.get()
    assert actual_vacancy.status == Vacancy.Status.PUBLISHED
    assert actual_vacancy.mentor == mentor
    assert actual_vacancy.required_qualifications.count() == 0
    assert actual_vacancy.direction == direction
    assert actual_vacancy.department == personnel.department
    assert actual_vacancy.reviewed_by == curator
    assert actual_vacancy.published_at is not None
    assert TestTask.objects.count() == 2
    test_task = TestTask.objects.get(title=vacancy_data["test_task"]["title"])
    assert test_task.description == vacancy_data["test_task"]["description"]
    assert test_task.type == vacancy_data["test_task"]["type"]
