import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_retrieve_trainee_profile(generic_api_client, trainee_profile):
    url = reverse(
        "trainee-profiles-detail", kwargs={"user_id": trainee_profile.user_id}
    )

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["user_id"] == trainee_profile.user_id
    assert response_data["citizenship"] == trainee_profile.citizenship_id
    assert response_data["bio"] == trainee_profile.bio
    assert response_data["phone_number"] == trainee_profile.phone_number


@pytest.mark.django_db
def test_list_trainee_profiles(generic_api_client, trainee_profile):
    url = reverse("trainee-profiles-list")

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    results = response_data
    assert len(results) == 1

    for data in results:
        assert "user_id" in data
        assert "citizenship" in data
        assert "bio" in data
        assert "phone_number" in data


@pytest.mark.django_db
def test_update_trainee_profile(api_client, user, non_preferable_country):
    url = reverse("trainee-profiles-detail", kwargs={"user_id": user.id})
    data = {
        "citizenship": non_preferable_country.id,
        "bio": "Updated trainee bio",
        "phone_number": "9876543210",
        "links": [{"url": "https://example.com/new-link"}],
        "educations": [
            {
                "name": "University B",
                "type": "university",
                "start_year": 2018,
                "end_year": 2022,
                "specialization": "Computer Science",
                "degree": "Master",
                "description": "Master's degree in Computer Science",
            }
        ],
        "work_experiences": [
            {
                "employer": "Company B",
                "position": "Software Developer",
                "start_date": "2023-01-01",
                "end_date": None,
                "description": "Worked on software development projects",
            }
        ],
    }

    response = api_client.patch(url, data, format="json")
    assert response.status_code == 200

    trainee_profile = user.trainee_profile
    trainee_profile.refresh_from_db()
    assert trainee_profile.citizenship == non_preferable_country
    assert trainee_profile.bio == "Updated trainee bio"
    assert trainee_profile.phone_number == "9876543210"
    assert trainee_profile.links.count() == 1
    assert trainee_profile.educations.count() == 1
    assert trainee_profile.work_experiences.count() == 1

    # Check the updated educations
    education = trainee_profile.educations.first()
    assert education.name == "University B"
    assert education.type == "university"
    assert education.start_year == 2018
    assert education.end_year == 2022
    assert education.specialization == "Computer Science"
    assert education.degree == "Master"
    assert education.description == "Master's degree in Computer Science"

    # Check the updated work experiences
    work_experience = trainee_profile.work_experiences.first()
    assert work_experience.employer == "Company B"
    assert work_experience.position == "Software Developer"
    assert work_experience.start_date.strftime("%Y-%m-%d") == "2023-01-01"
    assert work_experience.end_date is None
    assert work_experience.description == "Worked on software development projects"


@pytest.mark.django_db
def test_non_authenticate_update_trainee_profile(
    anon_api_client, user, non_preferable_country
):
    url = reverse("trainee-profiles-detail", kwargs={"user_id": user.id})
    data = {
        "citizenship": non_preferable_country.id,
        "bio": "Updated trainee bio",
        "phone_number": "9876543210",
        "links": [{"url": "https://example.com/new-link"}],
        "educations": [],
        "work_experiences": [],
    }

    response = anon_api_client.patch(url, data, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_update_not_own_trainee_profile(api_client, user2):
    url = reverse("trainee-profiles-detail", kwargs={"user_id": user2.id})
    data = {
        "citizenship": None,
        "bio": "Updated trainee bio",
        "phone_number": "9876543210",
        "links": [{"url": "https://example.com/new-link"}],
        "educations": [],
        "work_experiences": [],
    }

    response = api_client.patch(url, data, format="json")
    assert response.status_code == 403
