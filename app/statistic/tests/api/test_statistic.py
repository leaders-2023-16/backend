import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_candidate_statistics_api_view(
    internship_application,
    education,
    published_vacancy,
    work_experience1,
    work_experience2,
):
    client = APIClient()
    url = reverse("statistics")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Проверка наличия ключевых полей в ответе
    assert "responses" in data
    assert "age_statistics" in data
    assert "education" in data
    assert "work_experience" in data
    assert "direction_statistics" in data
    assert "vacancies" in data

    assert data["responses"] == {"total": 1, "relevant": 0, "irrelevant": 1}

    assert data["age_statistics"] == [
        {"label": 20, "count": 1},
    ]
    assert data["education"] == {
        "by_name": [{"count": 1, "label": "Test education"}],
        "by_type": [{"count": 1, "label": "university"}],
    }
    assert data["direction_statistics"] == [{"count": 1, "label": "Test direction"}]
    assert data["work_experience"] == [{"count": 1, "label": 2}]
    assert data["vacancies"]["total"] == 1
    assert data["vacancies"]["by_department"] == [{"count": 1, "label": "Department 1"}]


@pytest.mark.django_db
def test_candidate_statistics_empty_api_view(
    internship_application,
):
    client = APIClient()
    url = reverse("statistics")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
