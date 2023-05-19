import pytest
from django.urls import reverse
from internship.models import InternshipApplication
from rest_framework import status


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