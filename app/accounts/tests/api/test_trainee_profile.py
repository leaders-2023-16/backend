import pytest
from accounts.models import TraineeProfile, User
from django.urls import reverse


@pytest.fixture
def trainee2(create_user):
    return create_user(role=User.Role.TRAINEE, username="trainee2@user.com")


@pytest.fixture
def trainee_profile2(preferable_country, trainee2):
    profile = trainee2.trainee_profile
    profile.citizenship = preferable_country
    profile.cv_score = 100
    profile.test_score = 100
    profile.test_status = TraineeProfile.QualifyingStatus.PASSED
    profile.save()
    return profile


@pytest.mark.django_db
def test_retrieve_trainee_profile(generic_api_client, trainee_profile):
    url = reverse(
        "trainee-profiles-detail", kwargs={"user_id": trainee_profile.user_id}
    )

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["user_id"] == trainee_profile.user_id
    assert response_data["citizenship"]["id"] == trainee_profile.citizenship.id
    assert response_data["citizenship"]["name"] == trainee_profile.citizenship.name
    assert response_data["bio"] == trainee_profile.bio
    assert response_data["phone_number"] == trainee_profile.phone_number
    assert response_data["first_name"] == trainee_profile.user.first_name
    assert response_data["last_name"] == trainee_profile.user.last_name
    assert response_data["email"] == trainee_profile.user.email
    assert response_data["sex"] == trainee_profile.sex
    assert response_data["birth_date"] == trainee_profile.birth_date


@pytest.mark.django_db
def test_list_trainee_profiles(generic_api_client, trainee_profile):
    url = reverse("trainee-profiles-list")

    response = generic_api_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert "results" in response_data
    results = response_data["results"]
    assert len(results) == 1

    for data in results:
        assert "user_id" in data
        assert "citizenship" in data
        assert "bio" in data
        assert "phone_number" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert "sex" in data
        assert "birth_date" in data


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
        "sex": "M",
        "birth_date": "2023-05-21",
    }

    response = api_client.put(url, data, format="json")
    assert response.status_code == 200

    trainee_profile = user.trainee_profile
    trainee_profile.refresh_from_db()
    assert trainee_profile.citizenship == non_preferable_country
    assert trainee_profile.bio == "Updated trainee bio"
    assert trainee_profile.phone_number == "9876543210"
    assert trainee_profile.sex == "M"
    assert trainee_profile.birth_date is not None
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


@pytest.mark.django_db
def test_rating_list_trainee_profiles(curator_client, trainee_profile):
    url = reverse("trainee-profiles-rating")

    response = curator_client.get(url)
    assert response.status_code == 200
    response_data = response.json()
    assert "results" in response_data
    results = response_data["results"]
    assert len(results) == 0

    # Approve trainee to internship
    trainee_profile.test_status = TraineeProfile.QualifyingStatus.PASSED
    trainee_profile.save()

    response = curator_client.get(url)

    response_data = response.json()
    results = response_data["results"]
    assert len(results) == 1
    data = results[0]
    assert "user_id" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "email" in data
    assert "sex" in data
    assert "birth_date" in data
    assert "total_score" in data
    assert data["cv_score"] == trainee_profile.cv_score
    assert data["test_score"] == trainee_profile.test_score
    assert data["total_score"] == trainee_profile.test_score + trainee_profile.cv_score


@pytest.mark.django_db
def test_rating_list_trainee_profiles_sort(
    curator_client, trainee_profile, trainee_profile2
):
    # Approve trainee to internship
    trainee_profile.test_status = TraineeProfile.QualifyingStatus.PASSED
    trainee_profile.save()

    url = reverse("trainee-profiles-rating")

    response = curator_client.get(url)
    assert response.status_code == 200

    response_data = response.json()
    assert "results" in response_data
    results = response_data["results"]
    assert len(results) == 2
    assert results[0]["total_score"] > results[1]["total_score"]
