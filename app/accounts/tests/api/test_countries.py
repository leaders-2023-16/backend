import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_list_countries(generic_api_client, preferable_country, non_preferable_country):

    url = reverse("countries-list")

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 2

    country_names = [country["name"] for country in response_data["results"]]
    assert preferable_country.name in country_names
    assert non_preferable_country.name in country_names


@pytest.mark.django_db
def test_retrieve_country(generic_api_client, preferable_country):

    url = reverse("countries-detail", kwargs={"pk": preferable_country.id})

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == preferable_country.id
    assert response_data["name"] == preferable_country.name
