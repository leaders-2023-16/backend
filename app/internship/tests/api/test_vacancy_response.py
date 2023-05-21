import pytest
from django.urls import reverse
from internship.models import VacancyResponse
from rest_framework import status


@pytest.mark.django_db
def test_unauthorized_get_vacancy_responses(anon_api_client, internship_application):
    url = reverse("vacancy-responses-list")
    response = anon_api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_all_vacancy_responses(curator_client, vacancy_response):
    url = reverse("vacancy-responses-list")
    response = curator_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 1


@pytest.mark.django_db
def test_get_vacancy_responses(
    personnel_client, personnel, vacancy_response, department2
):
    url = reverse("vacancy-responses-list")
    response = personnel_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 1

    # change personnel department
    personnel.department = department2
    personnel.save()

    response = personnel_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 0


@pytest.mark.django_db
def test_create_vacancy_response(api_client, trainee, published_vacancy):
    url = reverse("vacancy-responses-list")
    data = {
        "vacancy": published_vacancy.id,
        "text_answer": "Some answer",
        "covering_letter": "Some answer",
    }

    response = api_client.post(url, data, format="json")

    # Assert that the request was successful and the object was created
    assert response.status_code == status.HTTP_201_CREATED
    assert VacancyResponse.objects.count() == 1
    vacancy_response = VacancyResponse.objects.get()
    assert vacancy_response.vacancy == published_vacancy
    assert vacancy_response.applicant == trainee.trainee_profile
    assert vacancy_response.text_answer == data["text_answer"]
    assert vacancy_response.covering_letter == data["covering_letter"]


@pytest.mark.django_db
def test_approve_vacancy_response_by_trainee(
    api_client, trainee, published_vacancy, vacancy_response
):
    url = reverse("vacancy-responses-detail", args=[vacancy_response.id])
    data = {
        "vacancy": published_vacancy.id,
        "text_answer": "Some answer",
        "covering_letter": "Some answer",
        "approved_by_applicant": True,
    }

    response = api_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert VacancyResponse.objects.count() == 1
    actual_vacancy_response = VacancyResponse.objects.get()
    assert actual_vacancy_response.vacancy == published_vacancy
    assert actual_vacancy_response.applicant == trainee.trainee_profile
    assert actual_vacancy_response.text_answer == vacancy_response.text_answer
    assert actual_vacancy_response.covering_letter == vacancy_response.covering_letter
    assert actual_vacancy_response.approved_by_applicant is True


@pytest.mark.django_db
def test_approve_vacancy_response_by_mentor(
    mentor_client, trainee, published_vacancy, vacancy_response
):
    url = reverse("vacancy-responses-detail", args=[vacancy_response.id])
    data = {
        "vacancy": published_vacancy.id,
        "text_answer": "Some answer",
        "covering_letter": "Some answer",
        "approved_by_mentor": True,
    }

    response = mentor_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert VacancyResponse.objects.count() == 1
    actual_vacancy_response = VacancyResponse.objects.get()
    assert actual_vacancy_response.vacancy == published_vacancy
    assert actual_vacancy_response.applicant == trainee.trainee_profile
    assert actual_vacancy_response.text_answer == vacancy_response.text_answer
    assert actual_vacancy_response.covering_letter == vacancy_response.covering_letter
    assert actual_vacancy_response.approved_by_mentor is True
