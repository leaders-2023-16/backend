import pytest
from accounts.models import User
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_registration(generic_api_client):
    url = reverse("sign-up")
    data = {
        "username": "testuser@us.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }

    # Отправка POST-запроса для регистрации пользователя
    response = generic_api_client.post(url, data, format="json")

    # Проверка кода ответа
    assert response.status_code == status.HTTP_201_CREATED

    # Проверка создания пользователя в базе данных
    assert User.objects.filter(username="testuser@us.com").exists()

    # Проверка наличия токенов в ответе
    assert "access" in response.data
    assert "refresh" in response.data

    assert response.data["user"]


@pytest.mark.django_db
def test_registration_existing_user(generic_api_client):
    url = reverse("sign-up")
    data = {
        "username": "testuser@us.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }
    User.objects.create_user(**data)

    # Отправка POST-запроса для регистрации пользователя
    response = generic_api_client.post(url, data, format="json")

    # Проверка кода ответа
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json() == {
        "username": ["A user with that username already exists."]
    }
