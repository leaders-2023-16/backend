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
    assert "access_token" in response.data
    assert "refresh_token" in response.data

    # Проверка наличия профиля стажера в ответе
    assert "trainee_profile" in response.data
    assert response.data["trainee_profile"]["first_name"] == "Test"
    assert response.data["trainee_profile"]["last_name"] == "User"


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
    assert response.status_code == status.HTTP_409_CONFLICT

    # Проверка создания пользователя в базе данных
    assert User.objects.filter(username="testuser@us.com").exists()

    assert response.data["detail"] == "USER_ALREADY_EXISTS"
