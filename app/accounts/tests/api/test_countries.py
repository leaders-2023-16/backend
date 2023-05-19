import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_list_countries(generic_api_client, country, country2):

    url = reverse("countries-list")

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 2

    country_names = [country["name"] for country in response_data]
    assert country.name in country_names
    assert country2.name in country_names


@pytest.mark.django_db
def test_retrieve_country(generic_api_client, country):

    url = reverse("countries-detail", kwargs={"pk": country.id})

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == country.id
    assert response_data["name"] == country.name
