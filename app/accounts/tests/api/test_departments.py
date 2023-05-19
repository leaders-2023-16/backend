import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_list_departments(generic_api_client, department, department2):

    url = reverse("departments-list")

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data["results"]) == 2

    department_names = [dep["name"] for dep in response_data["results"]]
    assert department.name in department_names
    assert department2.name in department_names


@pytest.mark.django_db
def test_retrieve_department(generic_api_client, department):

    url = reverse("departments-detail", kwargs={"pk": department.id})

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == department.id
    assert response_data["name"] == department.name
