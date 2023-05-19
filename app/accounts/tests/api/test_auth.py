import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_sign_in(generic_api_client):
    # Запрос на эндпоинт
    url = reverse("token_obtain_pair")
    data = {"username": "user@user.com", "password": "password"}
    response = generic_api_client.post(url, data, format="json")

    # Проверка статуса ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверка наличия токенов в ответе
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_refresh_token(generic_api_client):
    url = reverse("token_obtain_pair")
    data = {"username": "user@user.com", "password": "password"}
    response = generic_api_client.post(url, data, format="json")
    # Запрос на эндпоинт
    url = reverse("token_refresh")
    data = {"refresh": response.data["refresh"]}
    response = generic_api_client.post(url, data, format="json")

    # Проверка статуса ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверка наличия обновленного access-токена в ответе
    assert "access" in response.data
