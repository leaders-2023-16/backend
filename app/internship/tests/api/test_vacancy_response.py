import pytest
from django.urls import reverse
from internship.models import Vacancy, VacancyResponse, WorkPlace
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
def test_get_vacancies_filter(curator_client, vacancy_response):
    url = reverse("vacancy-responses-list")
    response = curator_client.get(url, {"vacancy": vacancy_response.vacancy.id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


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


@pytest.mark.django_db
def test_get_vacancy_response_by_vacancy(
    api_client, trainee, published_vacancy, vacancy_response
):
    url = reverse("vacancy-responses-by-vacancy", args=[published_vacancy.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "applicant" in data
    assert "vacancy" in data
    assert data["approved_by_mentor"] is None
    assert data["approved_by_applicant"] is None


@pytest.mark.django_db
def test_get_vacancy_response_approve(curator_client, vacancy_response):
    url = reverse("vacancy-responses-approve", args=[vacancy_response.id])
    response = curator_client.post(url)
    assert response.status_code == status.HTTP_201_CREATED
    assert WorkPlace.objects.count() == 1
    work_place = WorkPlace.objects.first()
    vacancy = vacancy_response.vacancy
    vacancy.refresh_from_db()
    assert work_place.vacancy == vacancy
    assert work_place.name == vacancy.name
    assert work_place.trainee == vacancy_response.applicant.user
    assert work_place.mentor == vacancy.mentor
    assert vacancy.status == Vacancy.Status.CLOSED
