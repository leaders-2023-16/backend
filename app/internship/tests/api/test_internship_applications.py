import pytest
from accounts.models import TraineeProfile, User
from django.urls import reverse
from internship.models import InternshipApplication
from rest_framework import status


@pytest.mark.django_db
def test_unauthorized_get_internship_applications(
    anon_api_client, internship_application
):
    url = reverse("internship-application-list")
    response = anon_api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_internship_applications(api_client, internship_application):
    url = reverse("internship-application-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 1
    assert data[0]["applicant"]["email"] == internship_application.applicant.email
    assert data[0]["status"] == internship_application.status
    assert data[0]["is_recommended"] is False


@pytest.mark.django_db
def test_get_internship_applications_with_filter(api_client, internship_application):
    url = reverse("internship-application-list")
    query = {"is_recommended": True}
    response = api_client.get(url, query)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 0

    query["is_recommended"] = False
    response = api_client.get(url, query)
    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == 1
    assert data[0]["applicant"]["email"] == internship_application.applicant.email
    assert data[0]["status"] == internship_application.status
    assert data[0]["is_recommended"] is False


@pytest.mark.django_db
def test_create_internship_application(candidate_client, user):
    url = reverse("internship-application-list")

    # Set up the data for the internship application
    data = {"user_id": user.id}

    # Make a POST request to create the internship application
    response = candidate_client.post(url, data, format="json")

    # Assert that the request was successful and the object was created
    assert response.status_code == status.HTTP_201_CREATED
    assert InternshipApplication.objects.count() == 1
    assert response.data["status"] == "pending"


@pytest.mark.django_db
def test_update_internship_application_by_candidate(
    candidate_client, internship_application
):
    # Set up the data for the update
    data = {
        "status": "approved",
    }

    url = reverse(
        "internship-application-detail", args=[internship_application.applicant_id]
    )

    # Make a PUT request to update the internship application
    response = candidate_client.put(url, data, format="json")

    # Assert that the request was forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_internship_application(curator_client, internship_application):
    # Set up the data for the update
    data = {
        "status": "approved",
    }

    url = reverse(
        "internship-application-detail", args=[internship_application.applicant_id]
    )

    # Make a PUT request to update the internship application
    response = curator_client.put(url, data, format="json")

    # Assert that the request was successful and the object was updated
    assert response.status_code == status.HTTP_200_OK
    assert (
        InternshipApplication.objects.get(pk=internship_application.applicant_id).status
        == "approved"
    )


@pytest.mark.django_db
def test_delete_internship_application(candidate_client, internship_application):
    url = reverse(
        "internship-application-detail", args=[internship_application.applicant_id]
    )

    # Make a DELETE request to delete the internship application
    response = candidate_client.delete(url)

    # Assert that the request was successful and the object was deleted
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not InternshipApplication.objects.filter(
        pk=internship_application.applicant_id
    ).exists()


@pytest.mark.django_db
def test_end_up_selection(curator_client, internship_application, trainee_profile):
    url = reverse("internship-application-end-up-selection")

    response = curator_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0

    trainee_profile.test_status = TraineeProfile.QualifyingStatus.PASSED
    trainee_profile.save()

    response = curator_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert InternshipApplication.objects.count() == 1
    internship_application.refresh_from_db()
    assert internship_application.status == InternshipApplication.Status.APPROVED
    assert internship_application.applicant.role == User.Role.TRAINEE
